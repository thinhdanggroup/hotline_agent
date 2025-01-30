.PHONY: start stop install clean

start:
	@echo "Starting FastAPI application..."
	@poetry run uvicorn src.hotline_agent.main:app --reload --port 8000 > app.log 2>&1 & echo $$! > app.pid
	@echo "Application started on http://localhost:8000"
	@echo "PID: $$(cat app.pid)"

stop:
	@if [ -f app.pid ]; then \
		echo "Stopping FastAPI application..."; \
		kill -9 `cat app.pid` || true; \
		rm app.pid; \
		echo "Application stopped"; \
	else \
		echo "No running application found"; \
	fi

install:
	@echo "Installing dependencies..."
	@poetry install

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -f app.pid app.log
	@echo "Cleanup complete"

.DEFAULT_GOAL := start
