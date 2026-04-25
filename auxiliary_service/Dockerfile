FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir flask requests python-dotenv gunicorn

COPY auxiliary_service/ /app/

CMD ["/bin/sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} 'app:create_app()'"]
