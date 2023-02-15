import functools
import os

from celery import Celery
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery('root')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


class atomic_celery_task:
    """
    This is a decorator we can use to add custom logic to our Celery task
    such as retry or database transaction
    """
    def __init__(self, *args, **kwargs):
        self.task_args = args
        self.task_kwargs = kwargs

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                with transaction.atomic():
                    return func(*args, **kwargs)
            except Exception as e:
                # task_func.request.retries
                raise task_func.retry(exc=e, countdown=3)

        task_func = app.task(*self.task_args, **self.task_kwargs)(wrapper_func)
        return task_func


@app.task(bind=True)
def debug_task(self):
    return 0
