#!/bin/sh

# Run migrations
python scripts/migrate.py

# Seed the database
python seed.py

# Start the application
exec uvicorn api:app --host 0.0.0.0 --port 8000 "$@" 