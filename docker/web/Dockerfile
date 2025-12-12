FROM python:3.13-slim AS builder

# Установка зависимостей системы
#RUN apt-get update && apt-get install -y \
#    libpq-dev \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app
RUN apt update && apt install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libzbar0 \
    libzbar-dev \
    && apt clean
# Копирование зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
#RUN apt-get update && apt-get install -y libzbar0

# Копируем весь проект
COPY . .

# Установка переменной окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE $PORT

# Запуск gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8080", "inriver_qr.wsgi:application"]


