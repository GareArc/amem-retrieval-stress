# A-mem Retrieval Evaluation

Tests whether [A-mem](https://github.com/WujiangXu/A-mem-sys)'s memory retrieval handles ambiguity, temporal reasoning, and indirect associations — known weak spots in embedding-based systems.

## Setup

```bash
git clone --recurse-submodules <repo-url>
cd memory-retrieval

python -m venv .venv && source .venv/bin/activate

# Apply DeepSeek compatibility patch to A-mem-sys
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

Set your LLM API key (needed for A-mem's memory analysis):

```bash
export OPENAI_API_KEY="sk-..."
# or OPENROUTER_API_KEY for OpenRouter
```

## Quick Start

```bash
# Run all 45 tests
python run_eval.py

# Run with verbose per-case metrics
python run_eval.py -v
```

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

## Switching Model / Provider

```bash
# OpenAI (default)
python run_eval.py --provider openai --model gpt-4o-mini

# Ollama (local, no API key needed)
python run_eval.py --provider ollama --model llama3

# DeepSeek (OpenAI-compatible, direct)
OPENAI_API_KEY="sk-your-deepseek-key" OPENAI_BASE_URL="https://api.deepseek.com" \
  python run_eval.py --provider openai --model deepseek-chat

# OpenRouter (any model including DeepSeek)
python run_eval.py --provider openrouter --model deepseek/deepseek-chat
python run_eval.py --provider openrouter --model anthropic/claude-3.5-sonnet

# SGLang
python run_eval.py --provider sglang --model meta-llama/Llama-3.1-8B-Instruct \
                   --sglang-host http://localhost --sglang-port 30000
```

## Tuning Retrieval

```bash
# Fewer results (stricter)
python run_eval.py --k 3

# Different embedding model
python run_eval.py --embedding-model all-mpnet-base-v2
```

## Output

Results print to console and save to JSON:

```bash
python run_eval.py -o results/run_001.json
```

The report compares `search()` (pure vector) vs `search_agentic()` (vector + link expansion) across all cases.

## Test Tiers

| Tier | Focus | Count | What It Tests |
|------|-------|-------|---------------|
| 1 | Ambiguity | 15 | Polysemy (Apple/apple, bank/bank), metonymy (Wall Street, Hollywood) |
| 2 | Temporal | 15 | Relative time ("tomorrow" → "today"), state conflicts, date arithmetic |
| 3 | Multi-hop | 15 | 2-hop chains, zero-overlap paraphrase, world knowledge, negation |

### Design Principles

- **No keyword leakage**: queries never share discriminating words with target memories. Connection requires understanding, not keyword matching.
- **Strong distractors**: each case includes 3-4 distractor memories that share topic/vocabulary with targets — only the tested dimension (ambiguity/time/inference) distinguishes them. Total of 135 distractors across all cases.
- **Both search methods**: every case runs `search()` and `search_agentic()` to isolate whether A-mem's link expansion helps.

## Metrics (per case)

| Metric | Meaning |
|--------|---------|
| Recall | Fraction of target memories found in top-k |
| Precision | Fraction of results that are targets |
| MRR | Reciprocal rank of first correct hit |
| Distractor contamination | Whether wrong-sense / outdated memories appear |

A case **passes** if all targets are retrieved AND no distractors contaminate results.

## Troubleshooting

### Request Timeout Errors

If you see "Request timed out" errors during tests:

1. **Patch applied?** The DeepSeek compatibility patch increases timeout to 120s and adds `OPENAI_BASE_URL` support. Re-apply if needed (see Setup).
2. **Slow API?** DeepSeek can be slower during peak hours. Consider using local Ollama instead:
   ```bash
   python run_eval.py --provider ollama --model llama3
   ```
3. **Network issues?** Check API connectivity or try a different provider (OpenRouter, OpenAI).

### Patch Updates

The `patches/deepseek-compat.patch` file may be updated occasionally. To sync:

```bash
git pull origin main                                # Get latest patch
cd A-mem-sys
git checkout agentic_memory/llm_controller.py      # Revert old changes
git apply ../patches/deepseek-compat.patch         # Apply updated patch
cd ..
```

## Project Structure

```
eval/
  fixtures.py   # 45 test cases with 135 total distractors
  runner.py     # EvaluationRunner pipeline
run_eval.py     # CLI entry point
A-mem-sys/      # Target system under test (submodule)
patches/        # Compatibility patches for A-mem-sys
  deepseek-compat.patch  # Adds timeout + base_url support
```
