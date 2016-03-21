import ast
import uuid
from ipware.ip import get_ip
from collections import defaultdict
import logging

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

from .serializers import SubmissionInputSerializer, SubmissionOutputSerializer
from .serializers import JobSerializer
from .models import Job, Submission, Backend
from .forms import SubmissionForm
from .tasks import *

logger = logging.getLogger(__name__)


class SubmissionDetails(mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        generics.GenericAPIView,
                        ):
    """
        API endpoint for Submission Viewing and Editing
    """
    # sub clean_input_data
    # TODO: function which grabs a regex from the db and ensures
    # the input data string passes
    # ValidationError(_('invalid_value'), code='invalid')
    queryset = Submission.objects.all()
    lookup_field = 'UUID'

    def __build_flags(self, task, request_data):
        flags = []
        params = task.parameters.all().filter(bool_valued=True)
        for param in params:
            if param.rest_alias in request_data and \
             request_data[param.rest_alias] == 'True':  # check what was passed
                flags.append(param.flag)
        return(flags)

    def __build_options(self, task, request_data):
        options = {}
        params = task.parameters.all().filter(bool_valued=False)
        for param in params:
            if param.rest_alias in request_data:
                options[param.flag] = request_data[param.rest_alias]
        return(options)

    def __test_params(self, steps, request_data):
        """
            Check that the list of additional params the tasks take
            has been provided by the user
        """
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
        request_contents = request.data
        if 'input_data' in request_contents:
            request_contents.pop('input_data')
        # # data['input_data'] = request.data['input_data']
        data = {}
        try:
            data['submission_name'] = request_contents.pop('submission_name')[0]
            data['email'] = request_contents.pop('email')[0]
            data['job'] = request_contents.pop('job')[0]
            data['ip'] = get_ip(request)
            data['UUID'] = str(uuid.uuid1())
        except MultiValueDictKeyError:
            raise MultiValueDictKeyError
        except KeyError:
            raise KeyError
        return(data, request_contents)

    def __construct_chain_string(self, steps, request_contents, UUID,
                                 job_priority):
        total_steps = len(steps)
        current_step = 1
        prev_step = None
        queue_name = 'celery'
        tchain = "chain("
        flags = {}
        options = {}
        for step in steps:
            flags = self.__build_flags(step.task, request_contents)
            options = self.__build_options(step.task, request_contents)
            if step.task.backend.server_type == Backend.LOCALHOST:
                queue_name = 'localhost'
            if step.task.backend.server_type == Backend.GRIDENGINE:
                queue_name = 'gridengine'
            if job_priority is Submission.LOW:
                queue_name = "low_"+queue_name
            if job_priority is Submission.HIGH:
                queue_name = "high_"+queue_name

            # tchain += "task_runner.si('%s',%i,%i,%i,'%s') | " \
            tchain += "task_runner.subtask(('%s', %i, %i, %i, '%s', %s, %s), " \
                      "immutable=True, queue='%s'), " \
                      % (UUID,
                         step.ordering,
                         current_step,
                         total_steps,
                         step.task.name,
                         flags,
                         options,
                         queue_name)
            current_step += 1
        tchain = tchain[:-2]
        tchain += ')()'
        logger.debug("TASK COMMAND: "+tchain)
        return(tchain)

    def post(self, request, *args, **kwargs):
        """
            This is the Job Submission endpoint.
            Here we add things to our data object, validate using the
            Submission Form because the serializer does NOT handle all
            the fields we save and push the job to the queue. We could
            write another serializer to handle this validation but that
            seems insane when the forms functionality is already in place
        """
        # # data['input_data'] = request.data['input_data']
        try:
            data, request_contents = self.__prepare_data(request)
        except MultiValueDictKeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # work out which job this refers to
        if Job.objects.filter(name=data['job']).exists():
            data['job'] = Job.objects.get(name=data['job']).pk
        else:
            content = {'error': 'Job name supplied does not exist'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Here we'll work out what priority this job will run at
        job_priority = settings.DEFAULT_JOB_PRIORITY
        subs = Submission.objects.filter(ip=data['ip'], status__lte=1)

        if len(subs) >= settings.QUEUE_HOG_SIZE:
            job_priority = Submission.LOW
        if len(subs) >= settings.QUEUE_HARD_LIMIT:
            content = {'error': "You have too many, "+str(len(subs))+", concurrent jobs running"}
            return Response(content, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if request.user.is_authenticated():
            job_priority = settings.LOGGED_IN_JOB_PRIORITY

        # In the future we'll set batch jobs to the lowest priority
        # TODO: VALIDATE input_data IN SOME MANNER
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
                content = {'error': "Required Parameter Missing. GET /analytics_automated/endpoints to discover all required options"}
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
                exec(tchain)
                logger.info('Sending This chain: '+tchain)
            except SyntaxError:
                logger.error('SyntaxError: Invalid string exec on: ' + tchain)
                return Response("MADE IT HERE2"+tchain, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error('500 Error: Invalid string exec on: ' + tchain)
                logger.error('500 Error' + str(e))
                return Response(tchain+"  "+str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        times = Submission.objects.values('job').annotate(time=Func(F('modified'), F('created'), function='age'))[:5000]
        results = defaultdict(lambda: [])
        for row in times:
            results[row['job']].append(int(row['time'].total_seconds()))
        for job in results:
            try:
                results[job] = int(sum(results[job])/len(results[job]))
            except Exception as e:
                results[job] = None
        return Response(results)


class JobList(mixins.ListModelMixin, generics.GenericAPIView):
    """
        API endpoint list the available job types on this service.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
