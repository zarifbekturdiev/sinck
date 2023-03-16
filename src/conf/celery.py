from __future__ import (
    absolute_import,
    unicode_literals,
)

import os

from celery import Celery
from celery.schedules import crontab
from constance import config


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('strana-sup')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run_sync_tasks': {
        'task': 'etl.run_sync_tasks',
        'schedule': crontab(minute='0', hour=f'*/{config.SYNCHRONIZATION_INTERVAL}'),
    },
}
