# Base stage with dependencies
FROM python:3.12-slim as base

# Install system dependencies for psycopg2, git, and PostgreSQL client tools
RUN apt-get update && \
    apt-get install -y libpq-dev gcc git curl postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies including dev dependencies (for testing)
RUN poetry install --no-root

# Production stage
FROM base as production

# Copy application code
COPY . .

# Run migrations, then start the app
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test stage - optimized for speed
FROM base as test

# Copy only test-related files
COPY app/tests/ ./app/tests/
COPY app/main.py ./app/main.py
COPY app/__init__.py ./app/__init__.py
COPY app/auth/ ./app/auth/
COPY app/config/ ./app/config/
COPY app/middleware/ ./app/middleware/
COPY app/routers/ ./app/routers/
COPY pytest.ini ./
COPY alembic.ini ./
COPY app/migrations/ ./app/migrations/
RUN mkdir -p static/default

# Default command for tests
CMD ["python3", "-m", "pytest", "app/tests/", "-v", "--tb=short"]