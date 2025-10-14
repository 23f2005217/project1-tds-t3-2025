FROM python:3.13-slim

# Set environment variables for Python and uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_INSTALL_DIR=/usr/local/bin \
    UV_CACHE_DIR=/app/.cache \
    PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create cache directory
RUN mkdir -p /app/.cache

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency files first for better caching
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Run the application
CMD ["uv", "run", "main.py"]

