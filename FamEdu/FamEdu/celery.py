import os
from celery.app import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamEdu.settings')

app = Celery()

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()