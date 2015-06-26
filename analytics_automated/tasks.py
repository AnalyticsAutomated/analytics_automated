from __future__ import absolute_import

import time

from celery import Celery
from celery import shared_task

from .models import Backend, Job, Submission, Task, Result, Parameter

@shared_task
def wait(t):
    """
        A task the waits. We'll use this for some trivial integration testing
    """
    time.sleep(t)
    return("passed")


@shared_task
def add(x, y):
    """
        The default tutorial example. Maybe use for integration testing
    """
    return x + y

# time limits?
@shared_task(default_retry_delay=5 * 60, rate_limit=40)
def task_runner(uuid, task_name):
    """
        Here is the action. Takes and task name and a job UUID. Gets the task
        config from the db and the job data and runs the job.
        Also needs to give control to whichever library supports the backend
        in question.
        Once the data is on the backend this task then just watches the
        backend until the job is done.
        Results are pushed to the frontend db but because they are files
        we just use the celery results for messaging and the results table
        for the files
    """
    s = Submission.objects.get(UUID=uuid)
    t = Task.objects.get(name=task_name)
    print(t.backend)
    print(Backend.LOCALHOST)
    if t.backend == Backend.LOCALHOST:
        print("Running at Localhost")
    if t.backend == Backend.GRIDENGINE:
        print("Pushing to GridEngine")
    if t.backend == Backend.RSERVE:
        print("Running at RServe")
