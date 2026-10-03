from app.worker import celery_app
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'publish-outbox-every-2-seconds': {
        'task': 'outbox_publisher',
        'schedule': 2.0,
    },
}
