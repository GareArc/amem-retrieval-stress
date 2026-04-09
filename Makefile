SESSION := amem-eval
MODEL ?= gpt-5-mini
CMD := python run_eval.py --provider openai --model $(MODEL)

OPENAI_API_KEY ?= sk-your-api-key-here
OPENAI_BASE_URL ?= https://api.openai.com/v1

VERBOSE ?=

run:
	@tmux new-session -d -s $(SESSION) "cd $(PWD) && if command -v uv > /dev/null 2>&1; then OPENAI_API_KEY='$(OPENAI_API_KEY)' OPENAI_BASE_URL='$(OPENAI_BASE_URL)' uv run $(CMD) $(VERBOSE) 2>&1 | tee eval_logs.txt; else source .venv/bin/activate && OPENAI_API_KEY='$(OPENAI_API_KEY)' OPENAI_BASE_URL='$(OPENAI_BASE_URL)' $(CMD) $(VERBOSE) 2>&1 | tee eval_logs.txt; fi" 2>/dev/null || \
		(echo "Session already running. Use 'make stop' first or 'make logs' to attach." && exit 1)
	@echo "Started. Run 'make logs' to follow output."

stop:
	@tmux kill-session -t $(SESSION) 2>/dev/null && echo "Stopped." || echo "No session running."

logs:
	@tmux attach -t $(SESSION) 2>/dev/null || echo "No session running. Use 'make run' to start."

status:
	@tmux has-session -t $(SESSION) 2>/dev/null && echo "Running." || echo "Not running."

patch:
	@cd A-mem-sys && git checkout agentic_memory/memory_system.py agentic_memory/llm_controller.py
	@cd A-mem-sys && git apply --whitespace=fix ../patches/deepseek-compat.patch
	@cd A-mem-sys && git apply --whitespace=fix ../patches/evolution-logging.patch
	@cd A-mem-sys && git apply --whitespace=fix ../patches/fix-links-deserialization.patch
	@echo "All patches applied."

.PHONY: run stop logs status patch
