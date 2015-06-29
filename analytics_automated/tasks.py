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
@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40)
def task_runner(self, uuid, step_id, current_step, total_steps, task_name):
    """
        Here is the action. Takes and task name and a job UUID. Gets the task
        config from the db and the job data and runs the job.
        Also needs to give control to whichever library supports the backend
        in question.
        Once the data is on the backend this task then just watches the
        backend until the job is done.d
        Results are pushed to the frontend db but because they are files
        we just use the celery results for messaging and the results table
        for the files
    """
    s = Submission.objects.get(UUID=uuid)
    t = Task.objects.get(name=task_name)
    # update submission tracking to note that this is running
    update_submission_state(s, True,
                            Submission.RUNNING,
                            step_id,
                            self.request.id,
                            'Running step :' + step_id)
    if t.backend.server_type == Backend.LOCALHOST:
        print("Running at Localhost")
        time.sleep(70)
        # 1. Make temp dir for results using the backend path provided and
        # the job uuid
        # 2. get the data and write it to a file in this temp dir
        # 3.
    # if t.backend.pk == Backend.GRIDENGINE:
    #     print("Pushing to GridEngine")
    # if t.backend.pk == Backend.RSERVE:
    #     print("Running at RServe")

    state = Submission.RUNNING
    if current_step == total_steps:
        state = Submission.COMPLETE

    update_submission_state(s, True,
                            Submission.RUNNING,
                            step_id,
                            self.request.id,
                            'Completed step :' + step_id)


def update_submission_state(s, claim, status, step, id, message):
    """
        Updates the Submission object with some book keeping
    """
    s.claimed = claim
    s.status = status
    s.message = message
    s.worker_id = id
    s.step_id = step
    s.save()
