# GenAI Stack Makefile

.PHONY: help install dev build start stop clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies for both frontend and backend
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev: ## Run both frontend and backend in development mode
	make -j 2 dev-backend dev-frontend

build: ## Build Docker images
	docker-compose build

start: ## Start all services with Docker Compose
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

clean: ## Clean up containers, volumes, and generated files
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/dist

test-backend: ## Run backend tests
	cd backend && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

migrate: ## Run database migrations
	cd backend && alembic upgrade head

setup: ## Initial setup - copy env files and install dependencies
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Please edit the .env files with your API keys"
	make install

docker-logs-backend: ## View backend container logs
	docker-compose logs -f backend

docker-logs-frontend: ## View frontend container logs
	docker-compose logs -f frontend

docker-shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

docker-shell-postgres: ## Open psql in postgres container
	docker-compose exec postgres psql -U postgres -d genai_stack
