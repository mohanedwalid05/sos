FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create migrations directory
RUN mkdir -p migrations

# Initialize Alembic if not already initialized
RUN if [ ! -f migrations/env.py ]; then alembic init migrations; fi

# Expose port
EXPOSE 8000 