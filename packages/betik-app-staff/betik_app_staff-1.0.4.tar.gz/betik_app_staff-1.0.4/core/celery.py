from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

from core import settings

app = Celery('betik_app_staff')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_email": {
        "task": "betik_app_email.tasks.send_email",
        "schedule": 10.0
    },

    "send_sms": {
        "task": "betik_app_sms.tasks.send_sms",
        "schedule": 10.0
    },

    "delete_expire_files": {
        "task": "betik_app_print_file.tasks.delete_expire_files",
        'schedule': crontab(hour=0, minute=0)
    }

}

app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': settings.ONCE_CELERY_BROKER_URL,
        'default_timeout': 2 * 60 * 60
    }
}
