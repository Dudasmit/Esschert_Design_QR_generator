#!/bin/sh
set -e
# Apply migrations
#python manage.py makemigrations products --noinput
python manage.py migrate --noinput


# Collect static files
python manage.py collectstatic --noinput

# Start server
#gunicorn inriver_qr.wsgi:application --bind 0.0.0.0:8000 --timeout 300
gunicorn inriver_qr.wsgi:application \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile /app/logs/access.log \
  --error-logfile /app/logs/error.log \
  --log-level info