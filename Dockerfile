# written by sounic behera
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies and clear apt cache
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies for the Celery Worker
RUN playwright install --with-deps chromium

# Copy the entire Python source code
COPY . .

# Ensure Python can import from /app
ENV PYTHONPATH=/app
