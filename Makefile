.PHONY: help install dev backend frontend clean test docker-build docker-up docker-down

help:
	@echo "Intent-Aware Network Stack - Available Commands"
	@echo ""
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start both backend and frontend in development mode"
	@echo "  make backend    - Start backend server only"
	@echo "  make frontend   - Start frontend dev server only"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean up build artifacts"
	@echo "  make docker-up  - Start with Docker Compose"
	@echo "  make docker-down - Stop Docker Compose"
	@echo ""

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	make -j 2 backend frontend

backend:
	cd backend && source venv/bin/activate && python -m app.main

frontend:
	cd frontend && npm run dev

test:
	@echo "Running backend tests..."
	cd backend && pytest ../tests/ -v

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/venv

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down