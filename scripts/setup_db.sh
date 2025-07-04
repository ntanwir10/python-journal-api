#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT >/dev/null 2>&1; then
    echo "Error: PostgreSQL is not running"
    exit 1
fi

# Create main database if it doesn't exist
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 ||
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER postgres -c "CREATE DATABASE $POSTGRES_DB"

# Create test database if it doesn't exist
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'test_journal_db'" | grep -q 1 ||
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER postgres -c "CREATE DATABASE test_journal_db"

# Create uuid-ossp extension if it doesn't exist (required for uuid_generate_v4())
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER test_journal_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo "Databases setup completed successfully"
