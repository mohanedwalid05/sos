#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install development requirements if in development mode
if [ "$ENVIRONMENT" = "development" ]; then
    pip install -r requirements.dev.txt
fi 