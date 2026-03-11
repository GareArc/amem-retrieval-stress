"""
Evaluation runner for A-mem memory retrieval tests.

Runs each test case in isolation (fresh memory system per case),
compares search() vs search_agentic(), and computes per-case + aggregate metrics.
"""

from __future__ import annotations

import json
import logging
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# Ensure A-mem-sys is importable
_AMEM_ROOT = Path(__file__).resolve().parent.parent / "A-mem-sys"
if str(_AMEM_ROOT) not in sys.path:
    sys.path.insert(0, str(_AMEM_ROOT))

from .fixtures import get_fixtures, NOISE_MEMORIES  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result data structures
# ---------------------------------------------------------------------------


@dataclass
class SearchMetrics:
    recall: float = 0.0
    precision: float = 0.0
    mrr: float = 0.0
    targets_found: int = 0
    targets_total: int = 0
    distractors_in_results: int = 0
    result_ids: list[str] = field(default_factory=list)
    result_contents: list[str] = field(default_factory=list)
    result_roles: list[str] = field(default_factory=list)
    result_scores: list[float] = field(default_factory=list)


@dataclass
class MemoryInput:
    fixture_id: str
    real_id: str
    content: str
    role: str
    timestamp: str = ""


@dataclass
class CaseResult:
    case_id: str
    tier: int
    category: str
    title: str
    query: str
    passed_search: bool = False
    passed_agentic: bool = False
    search_metrics: SearchMetrics = field(default_factory=SearchMetrics)
    agentic_metrics: SearchMetrics = field(default_factory=SearchMetrics)
    memories: list[MemoryInput] = field(default_factory=list)
    duration_seconds: float = 0.0
    error: str | None = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------


def _evaluate(
    case: dict[str, Any],
    results: list[dict[str, Any]],
    id_map: dict[str, str],
) -> SearchMetrics:
    """Score a set of search results against a test case's ground truth."""

    target_ids: set[str] = set()
    distractor_ids: set[str] = set()

    for mem in case["memories"]:
        real_id = id_map.get(mem["id"])
        if real_id is None:
            continue
        if mem["role"] == "target":
            target_ids.add(real_id)
        elif mem["role"] == "distractor":
            distractor_ids.add(real_id)
        # "support" memories count as targets (should be retrieved)
        elif mem["role"] == "support":
            target_ids.add(real_id)

    result_ids = [r["id"] for r in results]
    result_contents = [r.get("content", "")[:120] for r in results]
    result_scores = [r.get("score", 0.0) for r in results]

    noise_ids = {id_map[n["id"]] for n in NOISE_MEMORIES if n["id"] in id_map}

    result_roles: list[str] = []
    for rid in result_ids:
        if rid in target_ids:
            result_roles.append("target")
        elif rid in distractor_ids:
            result_roles.append("distractor")
        elif rid in noise_ids:
            result_roles.append("noise")
        else:
            result_roles.append("unknown")

    found = [rid for rid in result_ids if rid in target_ids]
    recall = len(found) / len(target_ids) if target_ids else 1.0

    if result_ids:
        true_positives = sum(1 for rid in result_ids if rid in target_ids)
        precision = true_positives / len(result_ids)
    else:
        precision = 0.0

    mrr = 0.0
    for i, rid in enumerate(result_ids):
        if rid in target_ids:
            mrr = 1.0 / (i + 1)
            break

    distractor_count = sum(1 for rid in result_ids if rid in distractor_ids)

    return SearchMetrics(
        recall=recall,
        precision=precision,
        mrr=mrr,
        targets_found=len(found),
        targets_total=len(target_ids),
        distractors_in_results=distractor_count,
        result_ids=result_ids,
        result_contents=result_contents,
        result_roles=result_roles,
        result_scores=result_scores,
    )


def _case_passed(metrics: SearchMetrics) -> bool:
    """A case passes if ALL targets are found AND no distractors contaminate results."""
    return metrics.recall >= 1.0 and metrics.distractors_in_results == 0


# ---------------------------------------------------------------------------
# Module-level runner (picklable for ProcessPoolExecutor)
# ---------------------------------------------------------------------------


def _run_case_isolated(config: dict[str, Any], case: dict[str, Any]) -> CaseResult:
    """Run a single test case in a fully isolated subprocess.

    This is a module-level function so ProcessPoolExecutor can pickle it.
    Each call creates its own AgenticMemorySystem (own ChromaDB in-memory client).
    """
    # Ensure A-mem-sys is importable in the subprocess
    amem_root = str(Path(__file__).resolve().parent.parent / "A-mem-sys")
    if amem_root not in sys.path:
        sys.path.insert(0, amem_root)

    # Re-import inside subprocess (module may not be loaded yet)
    from agentic_memory.memory_system import AgenticMemorySystem as AMS

    result = CaseResult(
        case_id=case["id"],
        tier=case["tier"],
        category=case["category"],
        title=case["title"],
        query=case["query"],
        notes=case.get("notes", ""),
    )

    t0 = time.time()

    try:
        system = AMS(
            model_name=config["embedding_model"],
            llm_backend=config["provider"],
            llm_model=config["model"],
            api_key=config["api_key"],
            sglang_host=config.get("sglang_host", "http://localhost"),
            sglang_port=config.get("sglang_port", 30000),
        )

        id_map: dict[str, str] = {}
        for mem in case["memories"]:
            kwargs: dict[str, Any] = {}
            if "timestamp" in mem:
                kwargs["time"] = mem["timestamp"]
            for key in ("keywords", "context", "tags"):
                if key in mem:
                    kwargs[key] = mem[key]

            real_id = system.add_note(mem["content"], **kwargs)
            id_map[mem["id"]] = real_id
            result.memories.append(
                MemoryInput(
                    fixture_id=mem["id"],
                    real_id=real_id,
                    content=mem["content"],
                    role=mem.get("role", "unknown"),
                    timestamp=mem.get("timestamp", ""),
                )
            )

        for noise in NOISE_MEMORIES:
            real_id = system.add_note(noise["content"])
            id_map[noise["id"]] = real_id

        search_results = system.search(case["query"], k=config["k"])
        agentic_results = system.search_agentic(case["query"], k=config["k"])

        result.search_metrics = _evaluate(case, search_results, id_map)
        result.agentic_metrics = _evaluate(case, agentic_results, id_map)
        result.passed_search = _case_passed(result.search_metrics)
        result.passed_agentic = _case_passed(result.agentic_metrics)

    except Exception as exc:
        result.error = f"{type(exc).__name__}: {exc}"

    result.duration_seconds = round(time.time() - t0, 2)
    return result


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


class EvaluationRunner:
    """Orchestrates the full evaluation pipeline."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        embedding_model: str = "all-MiniLM-L6-v2",
        k: int = 5,
        api_key: str | None = None,
        sglang_host: str = "http://localhost",
        sglang_port: int = 30000,
        verbose: bool = False,
        workers: int = 1,
    ) -> None:
        self.provider = provider
        self.model = model
        self.embedding_model = embedding_model
        self.k = k
        self.api_key = api_key
        self.sglang_host = sglang_host
        self.sglang_port = sglang_port
        self.verbose = verbose
        self.workers = max(1, workers)

    # ── Single case ───────────────────────────────────────────────────

    def _run_case(self, case: dict[str, Any]) -> CaseResult:
        """Run a single test case (delegates to module-level function)."""
        return _run_case_isolated(self._build_config(), case)

    # ── Full run ──────────────────────────────────────────────────────

    def run(
        self,
        tiers: list[int] | None = None,
        fixture_override: list[dict[str, Any]] | None = None,
    ) -> list[CaseResult]:
        """Run all (or selected tier) test cases and return results.

        Args:
            tiers: Only run fixtures from these tiers (default: all).
            fixture_override: If provided, run exactly these cases instead of
                loading from the fixtures module. Useful for single-case runs.
        """
        fixtures = (
            fixture_override if fixture_override is not None else get_fixtures(tiers)
        )
        results: list[CaseResult] = []
        total = len(fixtures)

        parallel = self.workers > 1
        print(f"\n{'=' * 70}")
        print(f"  A-MEM RETRIEVAL EVALUATION")
        print(f"  Provider: {self.provider} | Model: {self.model}")
        print(f"  Embedding: {self.embedding_model} | k={self.k}")
        print(f"  Test cases: {total} | Workers: {self.workers}")
        print(f"{'=' * 70}\n")

        if parallel:
            results = self._run_parallel(fixtures, total)
        else:
            results = self._run_sequential(fixtures, total)

        return results

    def _run_sequential(
        self, fixtures: list[dict[str, Any]], total: int
    ) -> list[CaseResult]:
        results: list[CaseResult] = []
        for i, case in enumerate(fixtures, 1):
            tag = f"[{i}/{total}] {case['id']}"
            print(f"  {tag:20s} {case['title'][:45]:45s} ", end="", flush=True)

            case_result = self._run_case(case)
            results.append(case_result)
            self._print_status(case_result)
        return results

    def _build_config(self) -> dict[str, Any]:
        """Build a plain dict of runner config (picklable for subprocesses)."""
        return {
            "provider": self.provider,
            "model": self.model,
            "embedding_model": self.embedding_model,
            "k": self.k,
            "api_key": self.api_key,
            "sglang_host": self.sglang_host,
            "sglang_port": self.sglang_port,
        }

    def _run_parallel(
        self, fixtures: list[dict[str, Any]], total: int
    ) -> list[CaseResult]:
        result_map: dict[str, CaseResult] = {}
        done_count = 0
        lock = threading.Lock()
        config = self._build_config()

        def _on_done(case_id: str, case_result: CaseResult) -> None:
            nonlocal done_count
            with lock:
                done_count += 1
                tag = f"[{done_count}/{total}] {case_result.case_id}"
                print(f"  {tag:20s} {case_result.title[:45]:45s} ", end="", flush=True)
                self._print_status(case_result)

        with ProcessPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(_run_case_isolated, config, case): case["id"]
                for case in fixtures
            }
            for future in as_completed(futures):
                case_id = futures[future]
                try:
                    case_result = future.result()
                except Exception as exc:
                    # Subprocess crashed entirely — create an error result
                    case_result = CaseResult(
                        case_id=case_id,
                        tier=0,
                        category="unknown",
                        title="(subprocess error)",
                        query="",
                        error=f"{type(exc).__name__}: {exc}",
                    )
                result_map[case_id] = case_result
                _on_done(case_id, case_result)

        return [result_map[case["id"]] for case in fixtures]

    def _print_status(self, r: CaseResult) -> None:
        if r.error:
            status = "ERR"
        elif r.passed_agentic:
            status = "PASS"
        elif r.agentic_metrics.recall > 0:
            status = "PARTIAL"
        else:
            status = "FAIL"

        print(f" {status:8s} ({r.duration_seconds:.1f}s)")

        if self.verbose and not r.passed_agentic:
            m = r.agentic_metrics
            print(
                f"           recall={m.recall:.2f}  precision={m.precision:.2f}  "
                f"mrr={m.mrr:.2f}  distractors={m.distractors_in_results}"
            )

    # ── Reporting ─────────────────────────────────────────────────────

    @staticmethod
    def report(results: list[CaseResult], output_path: str | None = None) -> None:
        """Print summary report and optionally save full JSON."""

        # ── Per-tier aggregation ──────────────────────────────────────
        tier_stats: dict[int, dict[str, Any]] = {}
        for r in results:
            t = r.tier
            if t not in tier_stats:
                tier_stats[t] = {
                    "total": 0,
                    "pass_search": 0,
                    "pass_agentic": 0,
                    "recall_search": [],
                    "recall_agentic": [],
                    "mrr_search": [],
                    "mrr_agentic": [],
                    "errors": 0,
                }
            s = tier_stats[t]
            s["total"] += 1
            s["pass_search"] += int(r.passed_search)
            s["pass_agentic"] += int(r.passed_agentic)
            s["recall_search"].append(r.search_metrics.recall)
            s["recall_agentic"].append(r.agentic_metrics.recall)
            s["mrr_search"].append(r.search_metrics.mrr)
            s["mrr_agentic"].append(r.agentic_metrics.mrr)
            if r.error:
                s["errors"] += 1

        tier_names = {1: "AMBIGUITY", 2: "TEMPORAL", 3: "MULTI-HOP"}

        def _avg(lst: list[float]) -> float:
            return sum(lst) / len(lst) if lst else 0.0

        # ── Console output ────────────────────────────────────────────
        print(f"\n{'=' * 70}")
        print(f"{'EVALUATION RESULTS':^70s}")
        print(f"{'=' * 70}")
        print()

        header = f"  {'Tier':<25s} {'search()':>12s} {'search_agentic()':>18s}"
        print(header)
        print(f"  {'-' * 60}")

        total_pass_s, total_pass_a, grand_total = 0, 0, 0

        for t in sorted(tier_stats):
            s = tier_stats[t]
            name = f"Tier {t}: {tier_names.get(t, '???')}"
            ps = s["pass_search"]
            pa = s["pass_agentic"]
            n = s["total"]
            total_pass_s += ps
            total_pass_a += pa
            grand_total += n
            print(
                f"  {name:<25s} {ps:>4d}/{n} ({100 * ps / n:5.1f}%)  {pa:>6d}/{n} ({100 * pa / n:5.1f}%)"
            )

        print(f"  {'-' * 60}")
        print(
            f"  {'OVERALL':<25s} {total_pass_s:>4d}/{grand_total} ({100 * total_pass_s / grand_total:5.1f}%)  "
            f"{total_pass_a:>6d}/{grand_total} ({100 * total_pass_a / grand_total:5.1f}%)"
        )
        print()

        # ── Avg recall / MRR ──────────────────────────────────────────
        print(f"  {'':25s} {'Avg Recall':>12s} {'Avg MRR':>12s}")
        print(f"  {'-' * 50}")
        for t in sorted(tier_stats):
            s = tier_stats[t]
            name = f"Tier {t}: {tier_names.get(t, '???')}"
            print(
                f"  {name:<25s}"
                f"  S={_avg(s['recall_search']):.3f}  A={_avg(s['recall_agentic']):.3f}"
                f"  |  S={_avg(s['mrr_search']):.3f}  A={_avg(s['mrr_agentic']):.3f}"
            )
        print()

        # ── Failures detail ───────────────────────────────────────────
        failures = [r for r in results if not r.passed_agentic]
        if failures:
            print(f"  FAILURES (search_agentic): {len(failures)}/{grand_total}")
            print(f"  {'-' * 60}")
            for r in failures:
                m = r.agentic_metrics
                reason = (
                    r.error or f"recall={m.recall:.2f} dist={m.distractors_in_results}"
                )
                print(f"    {r.case_id:8s} {r.title[:40]:40s} {reason}")
            print()

        print(f"{'=' * 70}\n")

        # ── JSON dump ─────────────────────────────────────────────────
        if output_path:
            payload = {
                "summary": {
                    "total_cases": grand_total,
                    "pass_search": total_pass_s,
                    "pass_agentic": total_pass_a,
                    "tiers": {
                        str(t): {
                            "name": tier_names.get(t, "???"),
                            "total": s["total"],
                            "pass_search": s["pass_search"],
                            "pass_agentic": s["pass_agentic"],
                            "avg_recall_search": round(_avg(s["recall_search"]), 4),
                            "avg_recall_agentic": round(_avg(s["recall_agentic"]), 4),
                            "avg_mrr_search": round(_avg(s["mrr_search"]), 4),
                            "avg_mrr_agentic": round(_avg(s["mrr_agentic"]), 4),
                            "errors": s["errors"],
                        }
                        for t, s in sorted(tier_stats.items())
                    },
                },
                "cases": [asdict(r) for r in results],
            }
            Path(output_path).write_text(
                json.dumps(payload, indent=2, ensure_ascii=False)
            )
            print(f"  Full results saved to: {output_path}")

            md_path = output_path.rsplit(".", 1)[0] + ".md"
            _write_markdown_report(results, tier_stats, tier_names, md_path)
            print(f"  Detailed report saved to: {md_path}\n")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

TIER_NAMES = {1: "Ambiguity", 2: "Temporal", 3: "Multi-hop"}
ROLE_ICON = {
    "target": "TARGET",
    "distractor": "DISTR",
    "support": "TARGET",
    "noise": "NOISE",
    "unknown": "?",
}
VERDICT_ICON = {"PASS": "PASS", "PARTIAL": "PARTIAL", "FAIL": "FAIL", "ERR": "ERR"}


def _verdict(r: CaseResult) -> str:
    if r.error:
        return "ERR"
    if r.passed_agentic:
        return "PASS"
    if r.agentic_metrics.recall > 0:
        return "PARTIAL"
    return "FAIL"


def _avg(lst: list[float]) -> float:
    return sum(lst) / len(lst) if lst else 0.0


def _write_markdown_report(
    results: list[CaseResult],
    tier_stats: dict[int, dict[str, Any]],
    tier_names: dict[int, str],
    path: str,
) -> None:
    lines: list[str] = []
    w = lines.append

    w("# A-mem Retrieval Evaluation Report\n")

    w("## How to Read This Report\n")
    w(
        "Each test case stores a set of **memories** (with known roles) into A-mem, "
        "then runs a **query** designed to require understanding beyond keyword matching. "
        "We compare what the system retrieved against ground truth.\n"
    )
    w("**Two search methods are compared side by side:**\n")
    w("- `search()` -- pure vector similarity (ChromaDB cosine distance)")
    w("- `search_agentic()` -- vector similarity + associative link expansion\n")
    w(
        "**Score** is ChromaDB's cosine distance. **Lower = more relevant.** "
        "A score of 0.8 is a better match than 1.4.\n"
    )
    w("**Metrics (computed per case):**\n")
    w("| Metric | Meaning |")
    w("|--------|---------|")
    w(
        "| Recall | Fraction of target memories found in top-k results (1.0 = all found) |"
    )
    w(
        "| Precision | Fraction of returned results that are actual targets (1.0 = no noise) |"
    )
    w(
        "| MRR | Reciprocal rank of the first correct result (1.0 = correct result ranked #1) |"
    )
    w(
        "| Distractors | Count of wrong-sense / outdated memories that appeared in results |"
    )
    w("")
    w("**Verdict:**\n")
    w("- **PASS** -- all targets retrieved, zero distractors")
    w(
        "- **PARTIAL** -- some targets found, but missing results or distractor contamination"
    )
    w("- **FAIL** -- no targets retrieved")
    w("- **ERR** -- test case encountered a runtime error\n")
    w("**Memory roles in tables:**\n")
    w("- **TARGET** -- this memory *should* be retrieved for the query")
    w(
        "- **DISTR** -- this memory shares vocabulary with the target but is the *wrong* answer"
    )
    w(
        "- **NOISE** -- one of 20 unrelated filler memories loaded per case to force discrimination\n"
    )

    w("## Shared Noise Corpus\n")
    w(
        "These 20 unrelated memories are added alongside each case's test memories. "
        "With k=5, the system must retrieve the right memories from ~22 total.\n"
    )
    w("| # | Content |")
    w("|---|---------|")
    for i, n in enumerate(NOISE_MEMORIES, 1):
        w(f"| {i} | {n['content']} |")
    w("")

    w("## Summary\n")
    w(
        "| Tier | Pass (search) | Pass (agentic) | Avg Recall (S) | Avg Recall (A) | Avg MRR (S) | Avg MRR (A) |"
    )
    w(
        "|------|--------------|----------------|----------------|----------------|-------------|-------------|"
    )
    total_s = total_a = grand = 0
    for t in sorted(tier_stats):
        s = tier_stats[t]
        n = s["total"]
        ps, pa = s["pass_search"], s["pass_agentic"]
        total_s += ps
        total_a += pa
        grand += n
        w(
            f"| **Tier {t}: {tier_names.get(t, '?')}** "
            f"| {ps}/{n} ({100 * ps / n:.0f}%) "
            f"| {pa}/{n} ({100 * pa / n:.0f}%) "
            f"| {_avg(s['recall_search']):.3f} "
            f"| {_avg(s['recall_agentic']):.3f} "
            f"| {_avg(s['mrr_search']):.3f} "
            f"| {_avg(s['mrr_agentic']):.3f} |"
        )
    w(
        f"| **Overall** "
        f"| {total_s}/{grand} ({100 * total_s / grand:.0f}%) "
        f"| {total_a}/{grand} ({100 * total_a / grand:.0f}%) "
        f"| | | | |"
    )
    w("")

    # ── Per-case detail ───────────────────────────────────────────
    current_tier = None
    for r in results:
        if r.tier != current_tier:
            current_tier = r.tier
            w(f"## Tier {current_tier}: {TIER_NAMES.get(current_tier, '?')}\n")

        v = _verdict(r)
        icon = VERDICT_ICON.get(v, "")
        w(f"### {icon} {r.case_id}: {r.title}\n")

        has_ts = any(m.timestamp for m in r.memories)
        w("**Case memories** (+ 20 shared noise memories above):\n")
        if has_ts:
            w("| Role | Timestamp | Content |")
            w("|------|-----------|---------|")
            for m in r.memories:
                role_icon = ROLE_ICON.get(m.role, "")
                ts = m.timestamp or "-"
                w(f"| {role_icon} | {ts} | {m.content} |")
        else:
            w("| Role | Content |")
            w("|------|---------|")
            for m in r.memories:
                role_icon = ROLE_ICON.get(m.role, "")
                w(f"| {role_icon} | {m.content} |")
        w("")

        w(f"**Query:** {r.query}\n")

        from .fixtures import get_fixture_by_id as _get_fix

        fix = _get_fix(r.case_id)
        if fix and fix.get("query_timestamp"):
            w(f"**Query issued at:** {fix['query_timestamp']}\n")

        if r.error:
            w(f"> **Error:** `{r.error}`\n")
            w("---\n")
            continue

        # Results table for search_agentic
        w("**Results (`search_agentic`):**\n")
        am = r.agentic_metrics
        if am.result_contents:
            w("| # | Role | Score | Content |")
            w("|---|------|-------|---------|")
            for i, (content, role, score) in enumerate(
                zip(am.result_contents, am.result_roles, am.result_scores), 1
            ):
                role_icon = ROLE_ICON.get(role, "")
                score_str = f"{score:.4f}" if score else "-"
                w(f"| {i} | {role_icon} {role} | {score_str} | {content} |")
        else:
            w("_No results returned._")
        w("")

        # Results table for search
        w("<details><summary>Results (<code>search</code>)</summary>\n")
        sm = r.search_metrics
        if sm.result_contents:
            w("| # | Role | Score | Content |")
            w("|---|------|-------|---------|")
            for i, (content, role, score) in enumerate(
                zip(sm.result_contents, sm.result_roles, sm.result_scores), 1
            ):
                role_icon = ROLE_ICON.get(role, "")
                score_str = f"{score:.4f}" if score else "-"
                w(f"| {i} | {role_icon} {role} | {score_str} | {content} |")
        else:
            w("_No results returned._")
        w("\n</details>\n")

        # Metrics
        w(f"| Metric | search | search_agentic |")
        w(f"|--------|--------|----------------|")
        w(f"| Recall | {sm.recall:.2f} | {am.recall:.2f} |")
        w(f"| Precision | {sm.precision:.2f} | {am.precision:.2f} |")
        w(f"| MRR | {sm.mrr:.2f} | {am.mrr:.2f} |")
        w(
            f"| Distractors | {sm.distractors_in_results} | {am.distractors_in_results} |"
        )
        w(f"| **Verdict** | **{'PASS' if r.passed_search else 'FAIL'}** | **{v}** |")
        w("")

        if r.notes:
            w(f"> {r.notes}\n")

        w("---\n")

    Path(path).write_text("\n".join(lines), encoding="utf-8")
