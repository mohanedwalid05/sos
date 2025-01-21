FROM python:3.12-slim

# Build arguments can be passed during build time
ARG ENVIRONMENT=production

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
# ENVIRONMENT: Runtime environment, can be overridden by docker-compose
# PATH: Add venv binaries to path
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=${ENVIRONMENT} \
    PATH="/app/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files separately to leverage Docker cache
COPY requirements.txt .
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Install development requirements if in development mode
COPY requirements.dev.txt .
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
        . venv/bin/activate && \
        pip install --no-cache-dir -r requirements.dev.txt ; \
    fi

# Copy application code
COPY . .

# Create migrations directory if it doesn't exist
RUN mkdir -p migrations

# Runtime command using environment variable
CMD if [ "$ENVIRONMENT" = "development" ] ; then \
        python scripts/migrate.py && \
        python seed.py && \
        uvicorn api:app --host 0.0.0.0 --port 8000 --reload ; \
    else \
        python scripts/migrate.py && \
        python seed.py && \
        uvicorn api:app --host 0.0.0.0 --port 8000 ; \
    fi

# Expose port
EXPOSE 8000 