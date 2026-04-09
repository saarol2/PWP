FROM python:3.10 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv .venv
COPY pyproject.toml ./
RUN .venv/bin/pip install .
RUN .venv/bin/pip install gunicorn
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
CMD ["/bin/sh", "-c", "/app/.venv/bin/gunicorn --bind 0.0.0.0:${PORT:-8080} 'swimapi:create_app()'"]
