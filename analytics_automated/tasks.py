from __future__ import absolute_import

import time
from commandRunner.localRunner import *

from celery import Celery
from celery import shared_task

from django.core.files.uploadedfile import SimpleUploadedFile

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
    data = ''
    # if this is the first task in a chain get the input_data from submission
    # if this is not the first task get the input_data from the results
    if current_step == 0:
        s.input_data.open(mode='r')
        for line in s.input_data:
            data += line.decode(encoding='UTF-8')
        s.input_data.close()
    else:
        pass  # look in results for the previous output

    # update submission tracking to note that this is running
    update_submission_state(s, True,
                            Submission.RUNNING,
                            step_id,
                            self.request.id,
                            'Running step :' + str(step_id))

    # Now we run the task handing off the actual running to the commandRunner
    # library
    run = None
    if t.backend.server_type == Backend.LOCALHOST:
        print("Running at Localhost")
        run = localRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                          in_glob=t.in_glob, out_glob=t.out_glob,
                          command=t.executable, input_data=data)

    run.prepare()
    print(run.command)
    exit_status = run.run_cmd()

    # if the command ran with success we'll send the file contents to the
    # database.
    # TODO: For now we write everything to the file as utf-8 but we'll need to
    # handle binary data eventually
    if exit_status == 0:
        print(run.output_data)
        run.tidy()
        file = SimpleUploadedFile(uuid+"."+run.out_glob,
                                  bytes(run.output_data, 'utf-8'))
        r = Result.objects.create(submission=s, task=t,
                                  step=current_step, name=t.name,
                                  message='Result',
                                  result_data=file)
    # Update where we are in the steps to the submission table
    state = Submission.RUNNING
    if current_step == total_steps:
        state = Submission.COMPLETE

    update_submission_state(s, True,
                            state,
                            step_id,
                            self.request.id,
                            'Completed step :' + str(step_id))


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
