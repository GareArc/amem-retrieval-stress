#!/usr/bin/env python3
"""
CLI entry point for A-mem memory retrieval evaluation.

Usage examples:

  # Run all tiers with OpenAI gpt-4o-mini (default)
  python run_eval.py

  # Run only Tier 1 (ambiguity) tests
  python run_eval.py --tiers 1

  # Run Tiers 1 and 3 with a different model
  python run_eval.py --tiers 1 3 --model gpt-4o --provider openai

  # Use Ollama local backend
  python run_eval.py --provider ollama --model llama3

  # Use OpenRouter
  python run_eval.py --provider openrouter --model openai/gpt-4o-mini --api-key sk-or-...

  # Use SGLang local server
  python run_eval.py --provider sglang --model meta-llama/Llama-3.1-8B-Instruct \\
                     --sglang-host http://localhost --sglang-port 30000

  # Change retrieval depth and embedding model
  python run_eval.py --k 3 --embedding-model all-mpnet-base-v2

  # Verbose mode (show metrics for failed cases inline)
  python run_eval.py -v

  # Save results to custom path
  python run_eval.py --output results/run_001.json

  # Run a single test case by ID
  python run_eval.py --case T1-05

  # List all available test case IDs
  python run_eval.py --list
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path for eval package imports
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Also ensure A-mem-sys is importable
_AMEM_ROOT = _PROJECT_ROOT / "A-mem-sys"
if str(_AMEM_ROOT) not in sys.path:
    sys.path.insert(0, str(_AMEM_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A-mem Memory Retrieval Evaluation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Provider / Model ──────────────────────────────────────────────
    parser.add_argument(
        "--provider",
        choices=["openai", "ollama", "sglang", "openrouter"],
        default="openai",
        help="LLM backend for memory analysis/evolution (default: openai)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="LLM model name (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (or set OPENAI_API_KEY / OPENROUTER_API_KEY env var)",
    )

    # ── SGLang-specific ───────────────────────────────────────────────
    parser.add_argument("--sglang-host", default="http://localhost")
    parser.add_argument("--sglang-port", type=int, default=30000)

    # ── Embedding / retrieval ─────────────────────────────────────────
    parser.add_argument(
        "--embedding-model",
        default="all-MiniLM-L6-v2",
        help="Sentence transformer model for ChromaDB embeddings (default: all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of results to retrieve per query (default: 5)",
    )
    parser.add_argument(
        "--skip-llm-analysis",
        action="store_true",
        help="Skip LLM-based metadata generation, use pre-defined metadata instead (faster, no API calls)",
    )
    parser.add_argument(
        "--skip-evolution",
        action="store_true",
        help="Skip memory evolution (link creation), disables LLM calls during add_note() process_memory step",
    )

    # ── Test selection ────────────────────────────────────────────────
    parser.add_argument(
        "--tiers",
        nargs="+",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help="Run only specific tiers (default: all). Example: --tiers 1 3",
    )
    parser.add_argument(
        "--case",
        default=None,
        help="Run a single test case by ID (e.g. T1-05)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test case IDs and exit",
    )

    # ── Output ────────────────────────────────────────────────────────
    parser.add_argument(
        "--output",
        "-o",
        default="eval_results.json",
        help="Path for JSON results file (default: eval_results.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-case metrics inline during run",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=1,
        help="Parallel workers (default: 1, max recommended: 10)",
    )

    args = parser.parse_args()

    # ── Configure logging ─────────────────────────────────────────────
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.getLogger("agentic_memory.llm_controller").setLevel(logging.INFO)

    # ── List mode ─────────────────────────────────────────────────────
    if args.list:
        from eval.fixtures import ALL_FIXTURES

        tier_names = {1: "AMBIGUITY", 2: "TEMPORAL", 3: "MULTI-HOP"}
        current_tier = None
        for f in ALL_FIXTURES:
            if f["tier"] != current_tier:
                current_tier = f["tier"]
                print(f"\n  Tier {current_tier}: {tier_names.get(current_tier, '???')}")
                print(f"  {'─' * 55}")
            print(f"    {f['id']:8s} {f['title']}")
        print()
        return

    # ── Validate single-case ID early ────────────────────────────────
    single_case = None
    if args.case:
        from eval.fixtures import get_fixture_by_id

        single_case = get_fixture_by_id(args.case)
        if single_case is None:
            print(
                f"Error: test case '{args.case}' not found. Use --list to see available IDs."
            )
            sys.exit(1)

    # ── Run evaluation ────────────────────────────────────────────────
    from eval.runner import EvaluationRunner

    runner = EvaluationRunner(
        provider=args.provider,
        model=args.model,
        embedding_model=args.embedding_model,
        k=args.k,
        api_key=args.api_key,
        sglang_host=args.sglang_host,
        sglang_port=args.sglang_port,
        verbose=args.verbose,
        workers=args.workers,
        skip_llm_analysis=args.skip_llm_analysis,
        skip_evolution=args.skip_evolution,
    )

    if single_case is not None:
        results = runner.run(fixture_override=[single_case])
    else:
        results = runner.run(tiers=args.tiers)

    EvaluationRunner.report(results, output_path=args.output)


if __name__ == "__main__":
    main()
