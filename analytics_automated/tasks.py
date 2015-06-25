from __future__ import absolute_import

import time

from celery import Celery
from celery import shared_task

@shared_task
def trivial():
    time.sleep(10)
    return("passed")


@shared_task
def add(x, y):
    return x + y

# time limits?
@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40)
def job_runner():
    return("passing")
