from flask import current_app
from celery import Celery

from studygovernor import create_app
from studygovernor.callbacks.backends.celery_backend import task_callback

app = create_app()

with app.app_context():
    celery = Celery('studygovernor_callbacks',
                    backend=current_app.config['STUDYGOV_CELERY_BACKEND'],
                    broker=current_app.config['STUDYGOV_CELERY_BROKER'])

    task = celery.task(bind=True)(task_callback)
