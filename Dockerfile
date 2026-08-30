# written by sounic behera
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies, curl, and lightweight system chromium
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to tell Playwright to use the system-installed Chromium binary
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Copy the entire Python source code
COPY . .

# Ensure Python can import from /app
ENV PYTHONPATH=/app