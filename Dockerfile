FROM python:3.10 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv .venv
COPY pyproject.toml ./
RUN .venv/bin/pip install .
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
ENV FLASK_APP=swimapi
CMD ["/bin/sh", "-c", "/app/.venv/bin/flask --app swimapi run --host=0.0.0.0 --port=${PORT:-8080}"]
