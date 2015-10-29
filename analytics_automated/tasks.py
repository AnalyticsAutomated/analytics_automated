from __future__ import absolute_import
import logging
import time
from commandRunner.localRunner import *

from celery import Celery
from celery import shared_task

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.conf import settings

from .models import Backend, Job, Submission, Task, Result, Parameter
from .models import BackendUser

logger = logging.getLogger(__name__)

try:
    from commandRunner.geRunner import *
except Exception as e:
    logger.info("SGE_ROOT AND DRMAA_LIBRARY_PATH ARE NOT SET; " +
                "GrideEngine backend not available")


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


def get_data(s, current_step):
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
        print("STEP"+str(previous_step))
        print(s)
        r = Result.objects.get(submission=s, step=previous_step)
        r.result_data.open(mode='r')
        for line in r.result_data:
            data += line.decode(encoding='UTF-8')
        r.result_data.close()
    return(data, previous_step)


# time limits?
@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40)
def task_runner(self, uuid, step_id, current_step,
                total_steps, task_name, flags, options):
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
    state = Submission.ERROR
    data, previous_step = get_data(s, current_step)
    iglob = t.in_glob.lstrip(".")
    oglob = t.out_glob.lstrip(".")
    data_dict = {uuid+"."+iglob: data}
    # update submission tracking to note that this is running
    Submission.update_submission_state(s, True, Submission.RUNNING, step_id,
                                       self.request.id,
                                       'About to run step: ' +
                                       str(current_step))

    # Now we run the task handing off the actual running to the commandRunner
    # library
    run = None
    # Here we get the users list and decide which one to submit the job with
    # TODO: Candidate to move to the command runner as it should handle the
    # finding out what is happening on the backend. Perhaps API call in
    # which returns the number of running processes and maybe the load average
    try:
        if t.backend.server_type == Backend.LOCALHOST:
            logger.info("Running At LOCALHOST")
            run = localRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                              out_globs=[t.out_glob, ],
                              command=t.executable,
                              input_data=data_dict,
                              flags=flags,
                              options=options,
                              input_string=uuid+"."+iglob,
                              output_string=uuid+"."+oglob)
        if t.backend.server_type == Backend.GRIDENGINE:
            logger.info("Running At GRIDENGINE")
            run = geRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                           out_globs=[t.out_glob, ],
                           command=t.executable,
                           input_data=data_dict,
                           flags=flags,
                           options=options,
                           std_out_string=uuid+".stdout",
                           input_string=uuid+"."+iglob,
                           output_string=uuid+"."+oglob)
    except Exception as e:
        cr_message = "Unable to initialise commandRunner: "+str(e)+" : " + \
                      str(current_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, cr_message)
        raise OSError(cr_message)

    try:
        run.prepare()
    except Exception as e:
        prep_message = "Unable to prepare files and tmp directory: "+str(e) + \
                       " : "+str(current_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, prep_message)
        raise OSError(prep_message)

    try:
        logger.info("EXECUTABLE: "+run.command)
        run.prepare()
        exit_status = run.run_cmd()
    except Exception as e:
        run_message = "Unable to call commandRunner.run_cmd(): "+str(e) + \
                      " : "+str(current_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, run_message)
        raise OSError(run_message)

    # if the command ran with success we'll send the file contents to the
    # database.
    # TODO: For now we write everything to the file as utf-8 but we'll need to
    # handle binary data eventually

    #if DEBUG settings are true we leave behind the temp working dir.
    if settings.DEBUG is not True:
        run.tidy()

    if exit_status == 0:
        file = None
        if run.output_data is not None:
            for fName, fData in run.output_data.items():
                file = SimpleUploadedFile(fName, bytes(fData, 'utf-8'))
                r = Result.objects.create(submission=s, task=t,
                                          step=current_step, name=t.name,
                                          message='Result',
                                          previous_step=previous_step,
                                          result_data=file)
    else:
        Submission.update_submission_state(s, True, Submission.ERROR, step_id,
                                           self.request.id,
                                           'Failed step, non 0 exit at step:' +
                                           str(step_id))
        logger.error("Command did not run: "+run.command)
        raise OSError("Command did not run: "+run.command)

    # Update where we are in the steps to the submission table
    state = Submission.RUNNING
    message = "Completed step: " + str(current_step)
    if current_step == total_steps:
        state = Submission.COMPLETE
        message = 'Completed job at step #' + str(current_step)
        # TODO: This needs a try-catch
        if s.email is not None and \
                len(s.email) > 5 and settings.DEFAULT_FROM_EMAIL is not None:
            send_mail(settings.EMAIL_SUBJECT_STRING+": "+uuid,
                      settings.EMAIL_MESSAGE_STRING+uuid, from_email=None,
                      recipient_list=[s.email],
                      fail_silently=False)
            logger.info("SENDING MAIL TO: "+s.email)

    Submission.update_submission_state(s, True, state, step_id,
                                       self.request.id, message)
