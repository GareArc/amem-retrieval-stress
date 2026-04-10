# A-mem Retrieval Evaluation

Tests whether [A-mem](https://github.com/WujiangXu/A-mem-sys)'s memory retrieval handles ambiguity, temporal reasoning, and indirect associations — known weak spots in embedding-based systems.

## Setup

```bash
git clone --recurse-submodules <repo-url>
cd memory-retrieval

python -m venv .venv && source .venv/bin/activate

# Apply patch to A-mem-sys (adds token tracking + DeepSeek support)
cd A-mem-sys && git apply ../patches/deepseek-compat.patch && cd ..

pip install -e A-mem-sys/
python -c "import nltk; nltk.download('punkt_tab', quiet=True)"
```

**If patch is already applied** (syncing on another machine):

```bash
cd A-mem-sys
git checkout agentic_memory/llm_controller.py  # Revert old patch
git apply ../patches/deepseek-compat.patch     # Apply updated patch
cd ..
```

## Quick Start

```bash
# Fastest mode — no LLM calls, pure vector search
python run_eval.py --skip-llm-analysis --skip-evolution

# Test link expansion (evolution only, requires API key)
export OPENAI_API_KEY="sk-..."
python run_eval.py --skip-llm-analysis

# Full mode — LLM metadata + evolution (slowest)
python run_eval.py
```

## OpenAI Configuration

```bash
export OPENAI_API_KEY="sk-..."

# Default: gpt-4o-mini
python run_eval.py --skip-llm-analysis

# Specify model
python run_eval.py --provider openai --model gpt-4o-mini --skip-llm-analysis
python run_eval.py --provider openai --model gpt-4o --skip-llm-analysis
```

The API key is only required when NOT using both `--skip-llm-analysis` and `--skip-evolution`.

## Selecting Tests

```bash
# By tier
python run_eval.py --tiers 1          # Ambiguity only
python run_eval.py --tiers 2 3        # Temporal + Multi-hop

# Single case
python run_eval.py --case T1-05 -v

# List all case IDs
python run_eval.py --list
```

## Other Providers

```bash
# Ollama (local, no API key needed)
python run_eval.py --provider ollama --model llama3

# DeepSeek (via OpenAI-compatible API)
OPENAI_API_KEY="sk-your-deepseek-key" OPENAI_BASE_URL="https://api.deepseek.com" \
  python run_eval.py --provider openai --model deepseek-chat

# OpenRouter
python run_eval.py --provider openrouter --model deepseek/deepseek-chat
python run_eval.py --provider openrouter --model anthropic/claude-3.5-sonnet

# SGLang
python run_eval.py --provider sglang --model meta-llama/Llama-3.1-8B-Instruct \
                   --sglang-host http://localhost --sglang-port 30000
```

## Tuning Retrieval

```bash
# Fewer results (stricter)
python run_eval.py --skip-llm-analysis --skip-evolution --k 3

# Different embedding model
python run_eval.py --skip-llm-analysis --skip-evolution --embedding-model all-mpnet-base-v2

# Parallel execution (faster for full suite)
python run_eval.py --skip-llm-analysis --skip-evolution --workers 4
```

## Output

Results print to console and save to JSON:

```bash
python run_eval.py -o results/run_001.json
```

The report compares `search()` (pure vector) vs `search_agentic()` (vector + link expansion) across all cases.

## Performance

**Three levels of LLM usage:**

#### Level 1: No LLM (Fastest)
```bash
python run_eval.py --skip-llm-analysis --skip-evolution
```
- No API calls, ~30 seconds for full suite
- Tests pure vector search (no link expansion)

#### Level 2: Evolution only (Recommended for agentic testing)
```bash
export OPENAI_API_KEY="sk-..."
python run_eval.py --skip-llm-analysis
```
- LLM calls for evolution only (link creation during memory loading)
- ~5-10 minutes for full suite
- Tests vector search + link expansion

#### Level 3: Full LLM
```bash
export OPENAI_API_KEY="sk-..."
python run_eval.py
```
- Full LLM usage: metadata generation + evolution
- ~1-4 hours for full suite

**What each flag does:**
- `--skip-llm-analysis`: Uses pre-defined keywords/context/tags from fixtures (skips `analyze_content()`)
- `--skip-evolution`: Skips link creation (disables `process_memory()`)

## Test Tiers

| Tier | Focus | Count | What It Tests |
|------|-------|-------|---------------|
| 1 | Ambiguity | 15 | Polysemy (Apple/apple, bank/bank), metonymy (Wall Street, Hollywood) |
| 2 | Temporal | 15 | Relative time ("tomorrow" → "today"), state conflicts, date arithmetic |
| 3 | Multi-hop | 15 | 2-hop chains, zero-overlap paraphrase, world knowledge, negation |

### Design Principles

- **No keyword leakage**: queries never share discriminating words with target memories. Connection requires understanding, not keyword matching.
- **Strong distractors**: each case includes 3-6 distractor memories sharing topic/vocabulary with targets — only the tested dimension distinguishes them. 180 distractors across all cases, with T3 cases having 6 distractors each to increase the chance of evolution link creation.
- **Minimal noise**: 5 off-topic noise memories per case (down from 20) so case-relevant memories dominate the neighbor pool during evolution.
- **Both search methods**: every case runs `search()` and `search_agentic()` to isolate whether A-mem's link expansion helps.

## Metrics (per case)

| Metric | Meaning |
|--------|---------|
| Recall | Fraction of target memories found in top-k |
| Precision | Fraction of results that are targets |
| MRR | Reciprocal rank of first correct hit |
| Distractor contamination | Whether wrong-sense / outdated memories appear |

A case **passes** if all targets are retrieved AND no distractors contaminate results.

## Patches

Patches in `patches/` are applied to the A-mem-sys submodule and tracked separately so the submodule stays on upstream HEAD.

| Patch | What it does |
|-------|-------------|
| `deepseek-compat.patch` | Adds token usage tracking, DeepSeek controller, OpenRouter support |
| `evolution-logging.patch` | Logs `should_evolve` decisions during memory insertion (debugging) |
| `fix-links-deserialization.patch` | Fixes ChromaDB JSON string deserialization for memory links in `search_agentic()` |
| `fix-agentic-neighbor-ranking.patch` | Fixes `search_agentic()` truncating neighbors before returning — now sorts all candidates by score and returns top-k |

To apply all patches:
```bash
cd A-mem-sys
git apply ../patches/deepseek-compat.patch
# Optional debugging patches:
git apply ../patches/evolution-logging.patch
git apply ../patches/fix-links-deserialization.patch
git apply ../patches/fix-agentic-neighbor-ranking.patch
cd ..
```

## Troubleshooting

### API key not found
```
ValueError: OpenAI API key not found
```
Set the environment variable before running:
```bash
export OPENAI_API_KEY="sk-..."
python run_eval.py --skip-llm-analysis
```

### Request Timeout Errors

If you see "Request timed out" errors:

1. Use fast mode: `python run_eval.py --skip-llm-analysis`
2. Check the patch is applied (adds 120s timeout). Re-apply if needed (see Setup).
3. Try a different provider: `--provider ollama` for local inference.

### Patch Updates

```bash
git pull origin main
cd A-mem-sys
git checkout agentic_memory/llm_controller.py
git apply ../patches/deepseek-compat.patch
cd ..
```

## Project Structure

```
eval/
  fixtures.py       # 45 test cases, 180 distractors, 5 noise memories
  runner.py         # EvaluationRunner pipeline
run_eval.py         # CLI entry point
A-mem-sys/          # Target system under test (submodule)
patches/            # Patches applied to A-mem-sys (submodule stays on upstream HEAD)
  deepseek-compat.patch          # Token tracking + DeepSeek/OpenRouter support
  evolution-logging.patch        # Debug: log evolution decisions
  fix-links-deserialization.patch # Fix: agentic search link traversal
```
