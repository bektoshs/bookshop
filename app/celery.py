import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Debug task')

app.conf.beat_schedule = {
    'add-every-1-hour': {
        'task': 'send_mail',
        'schedule': crontab(minute='*/1')
    }
}