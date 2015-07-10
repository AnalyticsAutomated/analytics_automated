import ast
import uuid
from ipware.ip import get_ip
import logging

from celery import chain

from django import forms
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

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

    def test_params(self, steps, request_data):
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

    def post(self, request, *args, **kwargs):
        """
            This is the Job Submission endpoint.
            Here we add things to our data object, validate using the
            Submission Form because the serializer does NOT handle all
            the fields we save and push the job to the queue. We could
            write another serializer to handle this validation but that
            seems insane when the forms functionality is already in place
        """
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
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
            # TODO : We could return a message specifying what is missing.

        # work out which job this refers to
        if Job.objects.filter(name=data['job']).exists():
            data['job'] = Job.objects.get(name=data['job']).pk
        else:
            content = {'error': 'Job name supplied does not exist'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        # TODO: VALIDATE input_data IN SOME MANNER
        submission_form = SubmissionForm(data, request.FILES)
        if submission_form.is_valid():
            s = submission_form.save()
            # Send to the Job Queue and set queued message if that is a success
            job = Job.objects.get(name=s.job)
            steps = job.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
            # 1. Look up tasks in a job
            # 2. Order tasks by their step id
            total_steps = len(steps)
            current_step = 1

            if not self.test_params(steps, request_contents):
                content = {'error': "Requied Parameter Missing"}
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

            if len(steps) == 0:
                content = {'error': "Job Requested Appears to have no Steps"}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            prev_step = None
            queue_name = 'celery'
            tchain = "chain("
            for step in steps:
                if step.task.backend.server_type == Backend.LOCALHOST:
                    queue_name = 'localhost'
                # tchain += "task_runner.si('%s',%i,%i,%i,'%s') | " \
                tchain += "task_runner.subtask(('%s',%i,%i,%i,'%s'), " \
                          "immutable=True, queue='%s'), " \
                          % (s.UUID,
                             step.ordering,
                             current_step,
                             total_steps,
                             step.task.name,
                             queue_name)
                current_step += 1

            # 3. Build Celery chain
            tchain = tchain[:-2]
            tchain += ')()'
            logger.debug("TASK COMMAND: "+tchain)
            try:
                exec(tchain)
            except SyntaxError:
                logger.error('SyntaxError: Invalid string exec on: ' + tchain)
            # 4. Call delay on the Celery chain

            content = {'UUID': s.UUID, 'submission_name': s.submission_name}
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {'error': submission_form.errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class JobList(mixins.ListModelMixin, generics.GenericAPIView):
    """
        API endpoint list the available job types on this service.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
