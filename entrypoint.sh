#!/bin/sh

# Apply migrations
#python manage.py makemigrations products --noinput
python manage.py migrate --noinput


# Collect static files
python manage.py collectstatic --noinput

# Start server
gunicorn inriver_qr.wsgi:application --bind 0.0.0.0:8000 --timeout 300
