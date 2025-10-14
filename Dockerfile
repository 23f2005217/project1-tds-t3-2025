FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_INSTALL_DIR=/usr/local/bin \
    PORT=5000

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY .env* /app/
COPY config.yaml /app/
COPY pyproject.toml /app/
COPY requirements.txt /app/

RUN uv pip install --system -r requirements.txt

COPY . /app/

EXPOSE 5000

CMD ["uv", "run", "main.py"]