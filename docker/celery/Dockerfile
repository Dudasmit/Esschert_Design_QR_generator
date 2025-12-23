FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        libzbar0 \
        libzbar-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запуск Celery worker
CMD ["celery", "-A", "inriver_qr.celery_app:app", "worker", "--loglevel=INFO"]
