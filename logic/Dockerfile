FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files separately to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create migrations directory if it doesn't exist
RUN mkdir -p migrations

# Expose port
EXPOSE 8000 

# Runtime command using environment variable
CMD python migrate.py && \
        python seed.py && \
        uvicorn api:app --host 0.0.0.0 --port 8000 --reload