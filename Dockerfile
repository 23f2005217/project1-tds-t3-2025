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

EXPOSE 3000

CMD ["uv", "run", "main.py"]
