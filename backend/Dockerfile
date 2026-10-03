FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client libs
RUN apt-get update && apt-get install -y libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn psycopg2-binary celery redis

COPY . .

# Run with Gunicorn using Uvicorn workers
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py"]
