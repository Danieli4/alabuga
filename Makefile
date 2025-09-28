.PHONY: help build migrate migrate-create start dev stop logs clean test lint format check-db reset-db shell

PYTHON ?= backend/.venv/bin/python

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker build commands
build: ## Build Docker containers
	docker compose build

# Database commands
migrate: build ## Run database migrations in Docker
	docker compose run --rm backend python -m app.db.init

migrate-create: ## Create a new migration (use NAME=migration_name)
	@if [ -z "$(NAME)" ]; then \
		echo "Usage: make migrate-create NAME=migration_name"; \
		exit 1; \
	fi
	docker compose run --rm backend alembic revision --autogenerate -m "$(NAME)"

migrate-upgrade: ## Upgrade to specific revision (use REV=revision_id)
	@if [ -z "$(REV)" ]; then \
		echo "Usage: make migrate-upgrade REV=revision_id"; \
		exit 1; \
	fi
	docker compose run --rm backend alembic upgrade "$(REV)"

migrate-downgrade: ## Downgrade to specific revision (use REV=revision_id) 
	@if [ -z "$(REV)" ]; then \
		echo "Usage: make migrate-downgrade REV=revision_id"; \
		exit 1; \
	fi
	docker compose run --rm backend alembic downgrade "$(REV)"

migrate-history: ## Show migration history
	docker compose run --rm backend alembic history

migrate-current: ## Show current migration revision
	docker compose run --rm backend alembic current

check-db: ## Check database connection and status
	docker compose run --rm backend python -c "from app.db.init import check_database_connection; print('✅ Database OK' if check_database_connection() else '❌ Database connection failed')"

reset-db: ## Reset database (remove and recreate)
	@echo "⚠️  This will remove all data! Are you sure? (y/N): "; \
	read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker compose down -v; \
		echo "🗑️  Database reset. Run 'make migrate' to recreate."; \
	else \
		echo "❌ Database reset cancelled."; \
	fi

reset-demo: ## Очистить демонстрационные данные (миссии, журнал, вложения)
	@if [ ! -x "$(PYTHON)" ]; then \
		echo "❌ Backend venv не найден. Выполните 'cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt'"; \
		exit 1; \
	fi
	PYTHONPATH=$(PWD) $(PYTHON) -m scripts.reset_demo_data

# Development commands
start: migrate ## Run migrations and start all services
	docker compose up -d

dev: migrate ## Run migrations and start services with logs
	docker compose up

start-no-migrate: build ## Start services without running migrations
	docker compose up -d

dev-no-migrate: build ## Start services with logs without migrations
	docker compose up

stop: ## Stop all Docker services
	docker compose down

restart: stop start ## Restart all services with migrations

# Utility commands
logs: ## Show Docker container logs
	docker compose logs -f

logs-backend: ## Show backend container logs only
	docker compose logs -f backend

logs-frontend: ## Show frontend container logs only
	docker compose logs -f frontend

shell: ## Open shell in backend Docker container
	docker compose exec backend /bin/bash

shell-run: ## Run a new backend container with shell access
	docker compose run --rm backend /bin/bash

# Testing and quality (run in Docker)
test: ## Run tests in Docker
	docker compose run --rm backend python -m pytest

test-verbose: ## Run tests with verbose output in Docker
	docker compose run --rm backend python -m pytest -v

lint: ## Run linting in Docker
	docker compose run --rm backend python -m ruff check .

format: ## Format code in Docker
	docker compose run --rm backend python -m ruff format .

# Cleanup commands
clean: ## Clean up Docker containers and images
	docker compose down --rmi local --volumes --remove-orphans

clean-all: ## Clean up all Docker resources (containers, images, volumes)
	docker compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Development workflow commands
setup: build migrate ## Initial setup: build containers and run migrations
	@echo "✅ Setup complete! Run 'make dev' to start the development server."

deploy-check: build lint test migrate ## Check if ready for deployment
	@echo "✅ Deployment checks passed!"

status: ## Show status of Docker services
	docker compose ps

# Production commands  
prod-start: migrate ## Start services in production mode (detached)
	docker compose up -d

prod-stop: ## Stop production services
	docker compose down

prod-restart: prod-stop prod-start ## Restart production services
