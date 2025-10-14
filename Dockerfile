FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_INSTALL_DIR=/usr/local/bin \
    UV_CACHE_DIR=/app/.cache \
    PORT=5000

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash xz-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /app/.cache

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && uv --version

COPY .env* /app/
COPY config.yaml /app/
COPY pyproject.toml /app/
COPY requirements.txt /app/

RUN uv sync

COPY . /app/

EXPOSE 5000

CMD ["uv", "run", "main.py"]

