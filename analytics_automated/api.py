import json
from ipware.ip import get_ip

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics

from .serializers import SubmissionSerializer, JobSerializer
from .models import Job, Submission


class Submission(mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    """
        API endpoint for Submission Viewing and Editing
    """
    # sub clean_input_data
    # TODO: function which grabs a regex from the db and ensures
    # the input data string passes
    # ValidationError(_('invalid_value'), code='invalid')
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class Job(mixins.ListModelMixin,
          generics.GenericAPIView):
    """
        API endpoint list the available job types on this service
    """
    # sub clean_input_data
    # TODO: function which grabs a regex from the db and ensures
    # the input data string passes
    # ValidationError(_('invalid_value'), code='invalid')
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# class SubmissionDetail(DetailEndpoint):
#     model = Submission
#
#
# class SubmissionCreate(Endpoint):
#
#     def post(self, request):
#         print("Hello")
#         # get the data from the post request
#         data = {}
#         data['input_data'] = request.FILES['input_data'].read().decode('UTF-8')
#         data['submission_name'] = request.FILES['submission_name'].read().decode('UTF-8')
#         data['email'] = request.FILES['email'].read().decode('UTF-8')
#         data['job_name'] = request.FILES['job_name'].read().decode('UTF-8')
#         data['ip'] = get_ip(request)
#
#         # work out which job this refers to
#         if Job.objects.filter(name=data['job_name']).exists():
#             data['job'] = Job.objects.get(name=data['job_name']).pk
#             del data['job_name']
#         else:
#             return {'error': 'Job name supplied does not exist'}
#         # TODO: VALIDATE input_data IN SOME MANNER
#
#         # validate and submit the data
#         submission_form = SubmissionForm(data)
#         if submission_form.is_valid():
#             s = submission_form.save()
#             fields = ('submission_name', 'message', 'UUID')
#             return serialize(s, fields)  # Should return a 201 code
#         else:
#             # TODO: get the error from form and return it here; form.errors()
#             return {'error': 'Input information is not correctly formatted'}
