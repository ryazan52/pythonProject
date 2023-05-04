import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newspaper.settings')

app = Celery('newspaper')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'mailing_every_mon_8am': {
        'task': 'news.tasks.monday_mailing',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),

    },
}