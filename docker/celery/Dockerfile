FROM python:3.12-slim

WORKDIR /app
RUN apt update && apt install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libzbar0 \
    libzbar-dev \
    && apt clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "inriver_qr.celery_app:app", "worker", "--loglevel=INFO"]
