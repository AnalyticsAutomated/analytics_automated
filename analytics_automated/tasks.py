from __future__ import absolute_import
import logging
import time
from commandRunner.localRunner import *

from celery import Celery
from celery import shared_task

from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Backend, Job, Submission, Task, Result, Parameter
from .models import BackendUser

logger = logging.getLogger(__name__)


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
def task_runner(self, uuid, step_id, current_step,
                total_steps, task_name, flags, options, priority):
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
    logger.info("TASK:" + task_name)
    logger.info("CURRENT STEP:" + str(current_step))
    logger.info("TOTAL STEPS:" + str(total_steps))
    logger.info("STEP ID:" + str(step_id))
    s = Submission.objects.get(UUID=uuid)
    t = Task.objects.get(name=task_name)
    data = ''
    previous_step = None
    # if this is the first task in a chain get the input_data from submission
    # if this is not the first task get the input_data from the results
    if current_step == 1:
        s.input_data.open(mode='r')
        for line in s.input_data:
            data += line.decode(encoding='UTF-8')
        s.input_data.close()
    else:
        previous_step = current_step-1
        r = Result.objects.get(submission=s, step=previous_step)
        r.result_data.open(mode='r')
        for line in r.result_data:
            data += line.decode(encoding='UTF-8')
        r.result_data.close()

    # update submission tracking to note that this is running
    Submission.update_submission_state(s, True, Submission.RUNNING, step_id,
                                       self.request.id,
                                       'Running step :' + str(step_id))

    # Now we run the task handing off the actual running to the commandRunner
    # library
    run = None
    # Here we get the users list and decide which one to submit the job with
    # TODO: Candidate to move to the command runner as it should handle the
    # finding out what is happening on the backend. Perhaps API call in
    # which returns the number of running processes and maybe the load average

    priority_value = getattr(BackendUser, priority)
    users = BackendUser.objects.all().filter(priority=priority_value)
    for user in users:
        print(user.login_name)

    if t.backend.server_type == Backend.LOCALHOST:
        logger.info("Running At LOCALHOST")
        run = localRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                          in_glob=t.in_glob, out_glob=t.out_glob,
                          command=t.executable, input_data=data, flags=flags,
                          options=options)
    logger.info("EXECUTABLE: "+run.command)
    run.prepare()
    exit_status = run.run_cmd()
    # if the command ran with success we'll send the file contents to the
    # database.
    # TODO: For now we write everything to the file as utf-8 but we'll need to
    # handle binary data eventually
    run.tidy()
    if exit_status == 0:
        file = None
        if run.output_data is not None:
            file = SimpleUploadedFile(uuid+"."+run.out_glob,
                                      bytes(run.output_data, 'utf-8'))
        r = Result.objects.create(submission=s, task=t,
                                  step=current_step, name=t.name,
                                  message='Result', previous_step=previous_step,
                                  result_data=file)
    else:
        Submission.update_submission_state(s, True, Submission.ERROR, step_id,
                                           self.request.id,
                                           'Failed step :' + str(step_id))
        logger.error("Command did not run: "+run.command)
        raise OSError("Command did not run: "+run.command)

    # Update where we are in the steps to the submission table
    state = Submission.RUNNING
    message = "Running"
    if current_step == total_steps:
        state = Submission.COMPLETE
        message = 'Completed at step #' + str(current_step)
        # TODO: Here we send and email to the user IF we have an email address
    Submission.update_submission_state(s, True, state, step_id, self.request.id,
                                       message)
