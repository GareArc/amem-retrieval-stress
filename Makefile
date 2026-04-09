SESSION := amem-eval
CMD := python run_eval.py --provider openai --model gpt-4o-mini

run:
	@tmux new-session -d -s $(SESSION) "source .venv/bin/activate && $(CMD)" 2>/dev/null || \
		(echo "Session already running. Use 'make stop' first or 'make logs' to attach." && exit 1)
	@echo "Started. Run 'make logs' to follow output."

stop:
	@tmux kill-session -t $(SESSION) 2>/dev/null && echo "Stopped." || echo "No session running."

logs:
	@tmux attach -t $(SESSION)

status:
	@tmux has-session -t $(SESSION) 2>/dev/null && echo "Running." || echo "Not running."

.PHONY: run stop logs status
