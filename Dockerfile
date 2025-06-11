# syntax=docker/dockerfile:1
# Build a minimal image to test Postgres connectivity

FROM python:3.11-slim AS runtime

# Avoid writing .pyc files and enable unbuffered output (helpful for logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./

# Default environment variables (can be overridden at runtime)
ENV RETRIES=3
ENV DELAY=5

ENTRYPOINT ["python", "-u", "./main.py"]
CMD ["--help"]
