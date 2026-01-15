FROM python:3.13-slim AS builder

# Установка рабочей директории
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
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Собираем статику
RUN python manage.py collectstatic --noinput



RUN chmod +x /app/entrypoint.sh
# Открываем порт (можно установить в .env)
EXPOSE 8000

# Запуск
ENTRYPOINT ["/app/entrypoint.sh"]
#CMD ["gunicorn", "-b", "0.0.0.0:8080", "inriver_qr.wsgi:application"]
