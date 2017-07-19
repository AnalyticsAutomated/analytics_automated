import ast
import uuid
from ipware.ip import get_ip
from collections import defaultdict
import pprint
import logging
import string
import keyword

from celery import chain

from django import forms
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from django.db.models import F, Func

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework import request
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser

from .serializers import SubmissionInputSerializer, SubmissionOutputSerializer
from .serializers import JobSerializer
from .models import Job, Submission, Backend
from .forms import SubmissionForm
from .tasks import *
from .validators import *
from .r_keywords import *
from .cmdline import *

logger = logging.getLogger(__name__)


class SubmissionDetails(mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        generics.GenericAPIView,
                        ):
    """
        API endpoint for Submission Viewing and Editing
    """
    queryset = Submission.objects.all()
    lookup_field = 'UUID'
    parser_classes = (MultiPartParser, FormParser,)

    def __build_params(self, task, request_data):
        params = []
        param_values = {}
        parameters = task.parameters.all().order_by("id")
        for param in parameters:
            if "VALUE" in param.flag:
                continue
            if param.bool_valued is True:
                # omit flag if user set false if not fail over to including it
                if param.rest_alias in request_data and \
                 request_data[param.rest_alias] == 'False':
                    params.append('')
                else:
                    params.append(param.flag)
            else:
                params.append(param.flag)
                if param.rest_alias in request_data:
                    param_values[param.flag] = {}
                    param_values[param.flag]['value'] = request_data[param.rest_alias]
                    param_values[param.flag]['switchless'] = param.switchless
                    param_values[param.flag]['spacing'] = param.spacing
                else:
                    param_values[param.flag] = {}
                    param_values[param.flag]['value'] = param.default
                    param_values[param.flag]['switchless'] = param.switchless
                    param_values[param.flag]['spacing'] = param.spacing

        return(params, param_values)

    def __return_value(self, task, request_data):
        options = {}
        params = task.parameters.all().filter(bool_valued=False)
        for param in params:
            if "VALUE" in param.flag:
                if param.rest_alias in request_data:
                    return request_data[param.rest_alias]
                else:
                    return param.default
        return ''

    def __build_environment(self, task):
        environment = {}
        envs = task.environment.all()
        for env in envs:
            environment[env.env] = env.value
        return(environment)

    def __test_params(self, steps, request_data):
        """
            Check that the list of additional params the tasks take
            has been provided by the user
        """
        if not self.__assess_param_membership(steps, request_data):
            return(False)

        if not self.__assess_param_value_sanity(steps, request_data):
            return(False)
        return(True)

    def __assess_param_value_sanity(self, steps, request_data):
        invalid = set(string.punctuation+string.whitespace)
        for field in request_data:
            if any(char in invalid for char in str(request_data[field])):
                return(False)  # don't allow punctuation chars
            for kw in keyword.kwlist:
                if kw in str(request_data[field]):
                    return(False)  # don't allow python keywords
            for kw in rkwlist:
                if kw in str(request_data[field]):
                    return(False)  # don't allow R keywords
            local_cmds = return_local_commands()
            for kw in local_cmds:
                if kw in str(request_data[field]):
                    return(False)  # don't allow unix commd
        return(True)

    def __assess_param_membership(self, steps, request_data):
        aliases = []
        for step in steps:
            params = Parameter.objects.filter(task=step.task)
            for param in params:
                aliases.append(param.rest_alias)
        if all(name in request_data for name in aliases):
            return(True)
        else:
            return(False)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubmissionOutputSerializer
        if self.request.method == 'POST':
            return SubmissionInputSerializer

    def get(self, request, *args, **kwargs):
        """
            Returns the current status of a job
        """
        return self.retrieve(request, *args, **kwargs)

    def __prepare_data(self, request):
        request_contents = request.data.dict()
        # print(request_contents)
        if 'input_data' in request_contents:
            request_contents.pop('input_data')
        # # data['input_data'] = request.data['input_data']
        data = {}
        try:
            data['submission_name'] = request_contents.pop('submission_name')
            data['email'] = request_contents.pop('email')
            data['job'] = request_contents.pop('job')
            data['ip'] = get_ip(request)
            data['UUID'] = str(uuid.uuid1())
        except MultiValueDictKeyError:
            raise MultiValueDictKeyError
        except KeyError:
            raise KeyError
        return(data, request_contents)

    def __construct_chain_string(self, steps, request_contents, UUID,
                                 job_priority):
        """
            Function takes all the step and task information for a given job
            and returns a valid celery string
        """
        total_steps = len(steps)
        chord_end = False
        current_step = 0
        step_counter = 1
        prev_step = None
        queue_name = 'celery'
        flags = {}
        options = {}
        value = ''

        if total_steps > 1:
            if steps[total_steps-1].ordering == steps[total_steps-2].ordering:
                total_steps += 1
                chord_end = True

        task_strings = {}
        # loop over steps and build the subtask string for each
        # track which have the same step priority
        # build group() for any which have equivalent priority
        # where priority list > 1
        # insert subtask or group in to chain()()

        for step in steps:
            (params, param_values) = self.__build_params(step.task, request_contents)
            value = self.__return_value(step.task, request_contents)
            environment = self.__build_environment(step.task)

            queue_name = str(step.task.backend.queue_type)
            if job_priority is Submission.LOW:
                queue_name = "low_"+queue_name
            if job_priority is Submission.HIGH:
                queue_name = "high_"+queue_name

            if step.ordering != prev_step:
                current_step += 1

            # tchain += "task_runner.si('%s',%i,%i,%i,'%s') | " \
            task_string = "task_runner.subtask(('%s', %i, %i, %i, %i, '%s', " \
                          "%s, %s, '%s', %i, %s), " \
                          "immutable=True, queue='%s')" \
                          % (UUID,
                             step.ordering,
                             current_step,
                             step_counter,
                             total_steps,
                             step.task.name,
                             params,
                             pprint.pformat(param_values).replace('\n',''),
                             value,
                             step.task.backend.queue_type.execution_behaviour,
                             environment,
                             queue_name)

            if step.ordering in task_strings:
                task_strings[step.ordering].append(task_string)
            else:
                task_strings[step.ordering] = [task_string]
            prev_step = step.ordering
            step_counter += 1

        tchain = "chain("
        for key in sorted(task_strings):
            if len(task_strings[key]) > 1:
                tchain += "group("
            for task_string in task_strings[key]:
                tchain += task_string+", "
            if len(task_strings[key]) > 1:
                tchain = tchain[:-2]
                tchain += "), "
        tchain = tchain[:-2]

        # This hack means that a job which ends in a chord won't complete
        # during the chord
        if chord_end is True:
            tchain += ", chord_end.subtask(('%s', %i, %i), " \
                      "immutable=True, queue='%s')" \
                      % (UUID, current_step, total_steps, queue_name)
        tchain += ',).apply_async()'

        # print(tchain)

        logger.debug("TASK COMMAND: "+tchain)
        return(tchain)

    def __get_job(self, job_name):
        if Job.objects.filter(name=job_name).exists():
            return Job.objects.get(name=job_name).pk
        else:
            raise ValueError

    def __get_job_priority(self, logged_in, ip_address):
        subs = Submission.objects.filter(ip=ip_address, status__lte=1)
        # logged in users get the priority given i settings or bumped down
        # by one if they have exceeded the soft limit
        priority = settings.DEFAULT_JOB_PRIORITY
        if logged_in:
            priority = settings.LOGGED_IN_JOB_PRIORITY

        if settings.QUEUE_HOG_SIZE is None and \
           settings.QUEUE_HARD_LIMIT is None:
            return priority, len(subs)

        if settings.QUEUE_HOG_SIZE is None and \
           settings.QUEUE_HARD_LIMIT >= 0:
            if len(subs) >= settings.QUEUE_HARD_LIMIT:
                return None, len(subs)
            else:
                return priority, len(subs)

        if settings.QUEUE_HOG_SIZE >= 0 and \
           settings.QUEUE_HARD_LIMIT is None:
            if len(subs) >= settings.QUEUE_HOG_SIZE:
                return priority-1, len(subs)
            else:
                return priority, len(subs)

        # anyone who excees the hardlimt gets bounced
        if len(subs) >= settings.QUEUE_HARD_LIMIT:
            return None, len(subs)

        if len(subs) >= settings.QUEUE_HOG_SIZE and \
           len(subs) < settings.QUEUE_HARD_LIMIT:
            if priority > 0:
                return priority-1, len(subs)
            else:
                return None, len(subs)

        return priority, len(subs)

    def post(self, request, *args, **kwargs):

        """
            This is the Job Submission endpoint.
            Here we add things to our data object, validate using the
            Submission Form because the serializer does NOT handle all
            the fields we save and push the job to the queue. We could
            write another serializer to handle this validation but that
            seems insane when the forms functionality is already in place
        """
        # data['input_data'] = request.data['input_data']
        try:
            data, request_contents = self.__prepare_data(request)
        except MultiValueDictKeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # work out which job this refers to
        try:
            data['job'] = self.__get_job(data['job'])
        except Exception as e:
            content = {'error': 'Job name supplied does not exist'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Find what priority queue the job should run on
        (job_priority, submission_number) = self.__get_job_priority(request.user.is_authenticated,
                                                                    data['ip'])
        if job_priority is None:
            content = {'error': "You have no authority to post jobs."
                                "Either you are not logged in too many, " +
                                str(submission_number) +
                                ", concurrent jobs running"}
            return Response(content, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # In the future we'll set batch jobs to the lowest priority
        submission_form = SubmissionForm(data, request.FILES)
        if submission_form.is_valid():
            s = submission_form.save()
            s.priority = job_priority
            s.save()
            # Send to the Job Queue and set queued message if that is a success
            job = Job.objects.get(name=s.job)

            steps = job.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
            # 1. Look up tasks in a job
            # 2. Order tasks by their step id

            # Check we have the params we want and then build the list of
            # params we'll pass to the task runner.
            if not self.__test_params(steps, request_contents):
                content = {'error': "Required Parameter Missing. GET "
                                    "/analytics_automated/endpoints to "
                                    "discover all required options"}
                s.delete()
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if len(steps) == 0:
                content = {'error': "Job Requested appears to have no Steps"}
                s.delete()
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            # 3. Build Celery chain
            tchain = self.__construct_chain_string(steps, request_contents,
                                                   s.UUID, job_priority)
            # 4. Call delay on the Celery chain
            try:
                logger.info('Sending this chain: '+tchain)
                exec(tchain)
            except SyntaxError:
                logger.error('SyntaxError: Invalid string exec on: ' + tchain)
                return Response(tchain,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error('500 Error: Invalid string exec on: ' + tchain)
                logger.error('500 Error' + str(e))
                return Response(tchain+"  "+str(e),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            content = {'UUID': s.UUID, 'submission_name': s.submission_name}
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {'error': submission_form.errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class Endpoints(generics.GenericAPIView):
    """
        returns the set of URIs to which jobs can be submitted
    """
    def get(self, request, *args, **kwargs):
        jobs = Job.objects.all()
        uris = []
        for job in jobs:
            uri_string = "/submission/&job="+str(job) + \
                         "&submission_name=[STRING]&email=[EMAIL_STRING]" + \
                         "&input_data=[FILE]"
            steps = job.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
            for step in steps:
                params = Parameter.objects.filter(task=step.task)
                for param in params:
                    if param.bool_valued is True:
                        uri_string += "&"+param.rest_alias+"=[TRUE/FALSE]"
                    else:
                        uri_string += "&"+param.rest_alias+"=[VALUE]"
            uris.append(uri_string)
        content = {"jobs": uris}
        return Response(content)


class JobTimes(generics.GenericAPIView):
    """
        Here we take a job name from the list of job names that an endpoint
        call allows and we return the average time in seconds that such a job
        takes
    """
    def get(self, request, *args, **kwargs):
        # Ok here we get the last 5000 results what we'd really like is
        # 500 results for each job types but I don't really want to
        # query the db once for each job type
        # Note there is a query for each job now so maybe this is rubbish
        times = Submission.objects.values('job').annotate(
                time=Func(F('modified'), F('created'), function='age'))[:5000]
        times_dict = defaultdict(lambda: [])
        for row in times:
            times_dict[row['job']].append(int(row['time'].total_seconds()))
        results = {}
        for job_id in times_dict:
            job_name = ''
            try:
                obj = Job.objects.get(pk=job_id)
                job_name = obj.name
                try:
                    obj = Job.objects.get(pk=job_id)
                    results[job_name] = int(sum(times_dict[job_id])/len(
                                        times_dict[job_id]))
                except Exception as e:
                    results[job_name] = None
            except Exception as e:
                logger.info('Attempting to get times for deleted job')
        return Response(results)


class JobList(mixins.ListModelMixin, generics.GenericAPIView):
    """
        API endpoint list the available job types on this service.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
