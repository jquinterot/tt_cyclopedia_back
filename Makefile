.PHONY: test dev lint format migrate install-hooks

# Run the full Docker test suite (same as CI)
test:
	docker-compose run --rm test

# Start development services (app + db + mongo)
dev:
	docker-compose up

# Run all linters (ruff + black --check)
lint:
	ruff check .
	black --check .

# Auto-fix formatting and linting issues
format:
	black .
	ruff check . --fix

# Run Alembic migrations against the current database
migrate:
	alembic upgrade head

# Install pre-commit hooks locally
install-hooks:
	pre-commit install
