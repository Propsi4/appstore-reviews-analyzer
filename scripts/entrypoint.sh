#!/bin/bash
set -e

# Wait for postgres to be ready
if [ "$POSTGRES__HOST" = "db" ]; then
  echo "Waiting for postgres at db:5432..."
  until pg_isready -h db -p 5432; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
  done
  echo "Postgres is up - executing command"
fi

# Run migrations (using the entrypoint in src/db/alembic)
echo "Running database migrations..."
# We need to be in the root to run alembic if configured that way
# Or specify the config file
poetry run alembic upgrade head

# Start the application
echo "Starting application with command: $@"
if [ "$1" = "api" ]; then
    exec poetry run api
else
    exec "$@"
fi
