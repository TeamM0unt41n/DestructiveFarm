from celery import Celery
from farm.config import config

celery_app = Celery('novara_farm', broker='pyamqp://celery_user:celery_password@rabbitmq//', include=['farm.submit_loop'])

celery_app.conf.beat_schedule = {
    f'submit_flags': {
        'task': 'farm.submit_loop.submit',
        'schedule': config.SUBMIT_PERIOD,
        'options': {'queue': 'flag_submition'},
    },
}