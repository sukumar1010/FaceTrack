FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=3

# Install only REQUIRED system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (better cache)
COPY requirements.txt .

# 🔥 CRITICAL: no pip cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Start app
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn facerec.wsgi:application --bind 0.0.0.0:8000

