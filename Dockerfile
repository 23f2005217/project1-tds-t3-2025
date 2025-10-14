FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml /app/
COPY . /app

FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /app /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN chmod +x /bin/uv
RUN mkdir -p /app/.local/share/uv /app/.cache/uv
RUN chmod -R 777 /app /app/.local /app/.cache

ENV UV_CACHE_DIR=/app/.cache/uv
ENV XDG_DATA_HOME=/app/.local/share

EXPOSE 5000

CMD ["uv", "run", "main.py"]
