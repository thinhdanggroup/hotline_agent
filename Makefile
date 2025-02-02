.PHONY: start stop install clean export-requirements

start:
	@echo "Starting FastAPI application..."
	@poetry run uvicorn src.main:app --reload --port 8080 > app.log 2>&1 & echo $$! > app.pid
	@echo "Application started on http://localhost:8000"
	@echo "PID: $$(cat app.pid)"

start-dev:
	@PORT=8080 VITE_API_URL=http://localhost:8080 ./script/run.sh

start-render:
	@poetry run uvicorn src.main:app --host 0.0.0.0 --port $PORT

update-version:
	@echo "Updating git version..."
	@echo "VITE_GIT_VERSION=$$(git rev-parse HEAD)" > src/ui/git-version.env
	@cd src/ui && ln -sf git-version.env .env

build: update-version
	@cd src/ui && npm install && npm run build

setup-git-hooks:
	@echo "Setting up git hooks..."
	@mkdir -p .git/hooks
	@echo '#!/bin/sh\nmake update-version' > .git/hooks/post-commit
	@echo '#!/bin/sh\nmake update-version' > .git/hooks/post-merge
	@chmod +x .git/hooks/post-commit .git/hooks/post-merge
	@echo "Git hooks installed successfully"

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
	@make setup-git-hooks

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -f app.pid app.log
	@echo "Cleanup complete"

docker-up:
	@docker compose up --build

docker-down:
	@docker compose down

clean-rooms:
	@python script/delete-rooms/app.py

export-requirements:
	@echo "Exporting all dependencies to requirements.txt..."
	@poetry export -f requirements.txt --output requirements.txt --without-hashes --with-credentials --with dev

export-vercel:
	@echo "Exporting minimal dependencies for Vercel deployment..."
	@echo "fastapi==0.115.7\nuvicorn[standard]==0.34.0\npython-dotenv==1.0.1\npydantic==2.10.6\naiohttp==3.11.11\ndaily-python==0.14.2\nopenai==1.59.9\ngoogle-generativeai==0.8.4" > requirements.txt

.DEFAULT_GOAL := start
