FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
COPY README.md .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Also install dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY tradewar/ /app/tradewar/
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.py

# Default command
CMD ["python", "scripts/run_simulation.py"]
