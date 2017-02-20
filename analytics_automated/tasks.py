from __future__ import absolute_import
import logging
import time
from commandRunner.localRunner import *

from celery import Celery
from celery import shared_task
from celery import group

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .models import Backend, Job, Submission, Task, Result, Parameter
from .models import BackendUser

logger = logging.getLogger(__name__)

try:
    from commandRunner.geRunner import *
except Exception as e:
    logger.info("SGE_ROOT AND DRMAA_LIBRARY_PATH ARE NOT SET; " +
                "GridEngine backend not available")

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


def get_data(s, uuid, current_step, in_globs):
    data_dict = {}
    data = ''
    previous_step = None
    # if this is the first task in a chain get the input_data from submission
    # if this is not the first task get the input_data from the results
    if current_step == 1:
        s.input_data.open(mode='r')
        for line in s.input_data:
            data += line.decode(encoding='UTF-8')
        s.input_data.close()
        local_glob = in_globs[0].lstrip(".")
        data_dict[uuid+"."+local_glob] = data
    else:
        previous_step = current_step-1
        # print("STEP"+str(previous_step))
        r = Result.objects.filter(submission=s, step=previous_step).all()
        for result in r:
            for glob in in_globs:
                if glob in result.result_data.name:
                    result.result_data.open(mode='r')
                    data = ""
                    for line in result.result_data:
                        data += line.decode(encoding='UTF-8')
                        data_dict[result.result_data.name] = data
                    result.result_data.close()

    return(data_dict, previous_step)

def insert_data(output_data, s, t, current_step, previous_step):
    if output_data is not None:
        # If not we trigger the No Outputs behaviour instead of pushing
        # the results to the db

        for fName, fData in output_data.items():
            # print("Writing Captured data")
            file = SimpleUploadedFile(fName, fData)
            logger.info("Result: Adding file to Results "+fName)
            r = Result.objects.create(submission=s, task=t,
                                      step=current_step, name=t.name,
                                      message='Result',
                                      previous_step=previous_step,
                                      result_data=file)
            logger.info("Result: File added")
    else:
        logger.info("Result: No files to add")
        r = Result.objects.create(submission=s, task=t,
                                  step=current_step, name=t.name,
                                  message='Result',
                                  previous_step=previous_step,
                                  result_data=None)


# time limits?
# step_id is the numerical value the user provides when they set the steps
#         in the UI
# current_step is a counter of where in the process we are, celery groups take
#              the same step value, which allows a subsequent step to get all
#              the results from the group
# step_counter a counter which counts which step this is in sequence used in
#              conjunction with total_steps to tell when a job has finished
# total_step   a totall of all the units of work/tasks that a job has
# TODO: Almost certainly a job can not end with a celery group(), some sort
#       of reduce step is 'required' this needs fix.
#       One way to handle this would be to add a dummy "end" task to the
#       chain() if the chain would otherwise end in a group()
@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40, max_retries=5)
def task_runner(self, uuid, step_id, current_step, step_counter,
                total_steps, task_name, params, param_values, value, environment):
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
    in_globs = "".join(t.in_glob.split()).split(",")
    out_globs = "".join(t.out_glob.split()).split(",")

    data_dict, previous_step = get_data(s, uuid, current_step, in_globs)
    iglob = in_globs[0].lstrip(".")
    oglob = out_globs[0].lstrip(".")
    # update submission tracking to note that this is running
    with transaction.atomic():
        if s.status != Submission.ERROR and s.status != Submission.CRASH:
            Submission.update_submission_state(s, True, Submission.RUNNING,
                                               step_id,
                                               self.request.id,
                                               'Running step: ' +
                                               str(current_step))
    stdoglob = ".stdout"
    if t.stdout_glob is not None and len(t.stdout_glob) > 0:
        stdoglob = "."+t.stdout_glob.lstrip(".")
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
            if value:
                run = localRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                              out_globs=out_globs,
                              in_globs=in_globs,
                              command=t.executable,
                              input_data=data_dict,
                              params=params,
                              param_values=param_values,
                              identifier=uuid,
                              std_out_str=uuid+stdoglob,
                              value_string=value,
                              env_vars=environment)
            else:
                run = localRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                              out_globs=out_globs,
                              in_globs=in_globs,
                              command=t.executable,
                              input_data=data_dict,
                              params=params,
                              param_values=param_values,
                              identifier=uuid,
                              std_out_str=uuid+stdoglob,
                              env_vars=environment)
        if t.backend.server_type == Backend.GRIDENGINE:
            logger.info("Running At GRIDENGINE")
            if value:
                run = geRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                           out_globs=out_globs,
                           in_globs=in_globs,
                           command=t.executable,
                           input_data=data_dict,
                           params=params,
                           param_values=param_values,
                           identifier=uuid,
                           std_out_str=uuid+stdoglob,
                           value_string=value,
                           env_vars=environment)
            else:
                run = geRunner(tmp_id=uuid, tmp_path=t.backend.root_path,
                           out_globs=out_globs,
                           in_globs=in_globs,
                           command=t.executable,
                           input_data=data_dict,
                           params=params,
                           param_values=param_values,
                           identifier=uuid,
                           std_out_str=uuid+stdoglob,
                           env_vars=environment)
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

    # set the valid exit statuses in case their is a defined value alternative
    valid_exit_status = [0, ]
    custom_exit_statuses = []
    if t.custom_exit_status is not None:
        statuses = t.custom_exit_status.replace(" ", "")
        try:
            if len(statuses) > 0:
                custom_exit_statuses = list(map(int, statuses.split(",")))
        except Exception as e:
            exit_status_message = "Exit statuses contains non-numerical and " \
                                  "other punctuation "+str(e) + \
                                  " : "+str(current_step) + " : " + run.command
            Submission.update_submission_state(s, True, state, step_id,
                                               self.request.id,
                                               exit_status_message)
            raise OSError(exit_status_message)
        if t.custom_exit_behaviour == Task.CONTINUE or \
           t.custom_exit_behaviour == Task.TERMINATE:
            valid_exit_status += custom_exit_statuses

    try:
        logger.info("EXECUTABLE: "+run.command)
        logger.info("STD OUT: "+run.std_out_str)
        # run.prepare()
        logger.info("EXIT STATUSES: "+str(valid_exit_status))
        exit_status = run.run_cmd(valid_exit_status)
    except Exception as e:
        run_message = "Unable to call commandRunner.run_cmd(): "+str(e) + \
                      " : "+str(current_step) + " : " + run.command
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, run_message)
        # We don't raise and error here as we want to test the exit status
        # and make a decision later
        raise OSError(run_message)

    # if the command ran with success we'll send the file contents to the
    # database.
    # TODO: For now we write everything to the file as utf-8 but we'll need to
    # handle binary data eventually

    # if DEBUG settings are true we leave behind the temp working dir.
    if settings.DEBUG is not True:
        run.tidy()

    custom_exit_termination = False
    incomplete_outputs_termination = False
    if exit_status in valid_exit_status:
        if exit_status in custom_exit_statuses and \
                       t.custom_exit_behaviour == Task.TERMINATE:
            custom_exit_termination = True

        found_endings = []
        if run.output_data is not None:
            for fName, fData in run.output_data.items():
                found_endings.append("."+fName.split(".")[-1])

        if set(out_globs).issubset(found_endings):
            insert_data(run.output_data, s, t, current_step, previous_step)
        else:
            if t.incomplete_outputs_behaviour == Task.FAIL:
                # insert what we have and then raise and error
                insert_data(run.output_data, s, t, current_step, previous_step)
                Submission.update_submission_state(s, True, state, step_id,
                                                   self.request.id,
                                                   "Failed with missing"
                                                   " outputs: " +
                                                   str(run.command))
                logger.error("Failed with missing outputs: "+str(run.command))
                raise OSError("Failed with missing outputs: "+str(run.command))
            if t.incomplete_outputs_behaviour == Task.TERMINATE:
                # insert what we have and end the job gracefully
                insert_data(run.output_data, s, t, current_step, previous_step)
                if self.request.chain:
                    self.request.chain = None
                incomplete_outputs_termination = True
            if t.incomplete_outputs_behaviour == Task.CONTINUE:
                # by default we insert whatever results we have and keep going
                insert_data(run.output_data, s, t, current_step, previous_step)
    elif exit_status in custom_exit_statuses and \
            t.custom_exit_behaviour == Task.FAIL:
            # if we hit an exit status that we ought to fail on raise an error
        insert_data(run.output_data, s, t, current_step, previous_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id,
                                           'Failed step, non 0 exit at step:' +
                                           str(step_id))
        logger.error("Exit Status " + str(exit_status) +
                     ": Failed with custom exit status: "+str(run.command))
        raise OSError("Exit Status " + str(exit_status) +
                      ": Failed with custom exit status: "+str(run.command))
    else:
        # Here we test the custom exit status. And do as it requires
        # skipping the regular raise() if needed
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id,
                                           'Failed step, non 0' +
                                           ' exit at step: ' +
                                           str(step_id) + ". Exit status:" +
                                           str(exit_status))
        logger.error("Exit Status " + str(exit_status) +
                     ": Command did not run: "+str(run.command))
        raise OSError("Exit Status " + str(exit_status) +
                      ": Command did not run: "+str(run.command))

    # decide if we should complete the job
    complete_job = False
    if custom_exit_termination:
        complete_job = True
    if incomplete_outputs_termination:
        complete_job = True
    if step_counter == total_steps:
        complete_job = True

    # Update where we are in the steps to the submission table
    state = Submission.RUNNING
    message = "Completed step: " + str(current_step)
    if complete_job:
        state = Submission.COMPLETE
        message = 'Completed job at step #' + str(current_step)
        # TODO: This needs a try-catch
        try:
            if s.email is not None and \
                    len(s.email) > 5 and \
                    settings.DEFAULT_FROM_EMAIL is not None:
                send_mail(settings.EMAIL_SUBJECT_STRING+": "+uuid,
                          settings.EMAIL_MESSAGE_STRING+uuid, from_email=None,
                          recipient_list=[s.email],
                          fail_silently=False)
            logger.info("SENDING MAIL TO: "+s.email)
        except Exception as e:
            logger.info("Mail server not available:" + str(e))

    # s2 = Submission.objects.get(UUID=uuid)
    s.refresh_from_db()
    if s.status != Submission.ERROR and s.status != Submission.CRASH:
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, message)

    if t.custom_exit_status is not None:
        if t.custom_exit_behaviour == Task.TERMINATE and exit_status in custom_exit_statuses:
            if self.request.chain:
                # print("hi there")
                self.request.chain = None


@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40)
def chord_end(self, uuid, step_id, current_step):
    s = Submission.objects.get(UUID=uuid)

    state = Submission.COMPLETE
    message = 'Completed job at step #' + str(current_step)
    # TODO: This needs a try-catch
    try:
        if s.email is not None and \
                len(s.email) > 5 and \
                settings.DEFAULT_FROM_EMAIL is not None:
            send_mail(settings.EMAIL_SUBJECT_STRING+": "+uuid,
                      settings.EMAIL_MESSAGE_STRING+uuid, from_email=None,
                      recipient_list=[s.email],
                      fail_silently=False)
        logger.info("SENDING MAIL TO: "+s.email)
    except Exception as e:
        logger.info("Mail server not available:" + str(e))

    s.refresh_from_db()
    if s.status != Submission.ERROR and s.status != Submission.CRASH:
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, message)
