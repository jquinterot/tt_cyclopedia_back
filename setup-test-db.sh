#!/bin/bash

set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Create test database if it doesn't exist
echo "Creating test database..."
psql -h db -U postgres -d postgres -c "CREATE DATABASE tt_cyclopedia_test;" 2>/dev/null || echo "Database already exists"

# Wait a moment for database to be fully ready
sleep 2

# Run migrations with retry logic
echo "Running migrations..."
max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if alembic upgrade head; then
        echo "Migrations completed successfully!"
        break
    else
        retry_count=$((retry_count + 1))
        echo "Migration failed, retrying... ($retry_count/$max_retries)"
        sleep 2
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to run migrations after $max_retries attempts"
    exit 1
fi

echo "Test database setup complete!" 