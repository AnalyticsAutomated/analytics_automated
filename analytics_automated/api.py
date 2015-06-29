import ast
import uuid
from ipware.ip import get_ip

from django import forms
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .serializers import SubmissionInputSerializer, SubmissionOutputSerializer
from .serializers import JobSerializer
from .models import Job, Submission
from .forms import SubmissionForm
from .tasks import *


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
        # # data['input_data'] = request.data['input_data']
        data = {}
        try:
            data['submission_name'] = request.data['submission_name']
            data['email'] = request.data['email']
            data['job'] = request.data['job']
            data['ip'] = get_ip(request)
            data['UUID'] = str(uuid.uuid1())
        except MultiValueDictKeyError:
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
            steps = job.steps.all().select_related('task').extra(order_by=['ordering'])
            # 1. Look up tasks in a job
            # 2. Order tasks by their step id
            total_steps = len(steps)-1
            current_step = 0
            chain = "("
            for step in steps:
                chain += "task_runner.si('%s','%i','%i','%i','%s') | " % (s.UUID,
                                                                          step.ordering,
                                                                          current_step,
                                                                          total_steps,
                                                                          step.task.name)
                current_step += 1

            chain = chain[:-3]
            chain += ')()'
            try:
                eval(chain)
            except SyntaxError:
                print('Invalid string eval on: ' + chain)
            # 3. Build Celery chain
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
