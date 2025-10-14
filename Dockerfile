FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt /app/

RUN python -m venv /app/venv

RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /app/venv /app/venv

COPY . /app

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 5000

CMD ["/app/venv/bin/python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
