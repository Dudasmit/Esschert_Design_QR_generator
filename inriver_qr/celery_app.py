# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inriver_qr.settings')

app = Celery('inriver_qr')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

