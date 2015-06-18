import ast
import uuid
from ipware.ip import get_ip

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .serializers import SubmissionInputSerializer, SubmissionOutputSerializer
from .serializers import JobSerializer
from .models import Job, Submission


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
            the fields we save and push the job to the queue
        """
        data = ast.literal_eval(request.data)
        # # data['input_data'] = request.data['input_data']
        data.update({'ip': get_ip(request)})
        data.update({'UUID': str(uuid.uuid1())})
        # work out which job this refers to
        if Job.objects.filter(name=data['job']).exists():
            data['job'] = Job.objects.get(name=data['job']).pk
        else:
            content = {'error': 'Job name supplied does not exist'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        # TODO: VALIDATE input_data IN SOME MANNER
        print(data)

        content = {'please move along': 'nothing to see here'}
        return Response(content, status=status.HTTP_201_CREATED)


class JobList(mixins.ListModelMixin, generics.GenericAPIView):
    """
        API endpoint list the available job types on this service.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

# class SubmissionCreate(Endpoint):
#
#     def post(self, request):
#         # get the data from the post request
#         data = {}
#         data['input_data'] = request.FILES['input_data'].read().decode('UTF-8')
#         data['submission_name'] = request.FILES['submission_name'].read().decode('UTF-8')
#         data['email'] = request.FILES['email'].read().decode('UTF-8')
#         data['job_name'] = request.FILES['job_name'].read().decode('UTF-8')
#         data['ip'] = get_ip(request)
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
