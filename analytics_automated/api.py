import json
from ipware.ip import get_ip

from django import forms
from django.http import HttpResponse

from restless.views import Endpoint
from restless.modelviews import ListEndpoint, DetailEndpoint
from restless.models import serialize

from .models import Job, Submission


class SubmissionForm(forms.ModelForm):

    # sub clean_input_data
    # TODO: function which grabs a regex from the db and ensures
    # the input data string passes
    # ValidationError(_('invalid_value'), code='invalid')

    class Meta:
        model = Submission
        fields = ['job', 'ip', 'email', 'submission_name']

# Useful for dev purposes but we don't want users to be able to get a list of
# everything
# class SubmissionList(ListEndpoint):
#     model = Submission


class SubmissionDetail(DetailEndpoint):
    model = Submission


class SubmissionCreate(Endpoint):

    def post(self, request):
        print("Hello")
        # get the data from the post request
        data = {}
        data['input_data'] = request.FILES['input_data'].read().decode('UTF-8')
        data['submission_name'] = request.FILES['submission_name'].read().decode('UTF-8')
        data['email'] = request.FILES['email'].read().decode('UTF-8')
        data['job_name'] = request.FILES['job_name'].read().decode('UTF-8')
        data['ip'] = get_ip(request)

        # work out which job this refers to
        if Job.objects.filter(name=data['job_name']).exists():
            data['job'] = Job.objects.get(name=data['job_name']).pk
            del data['job_name']
        else:
            return {'error': 'Job name supplied does not exist'}
        # TODO: VALIDATE input_data IN SOME MANNER

        # validate and submit the data
        submission_form = SubmissionForm(data)
        if submission_form.is_valid():
            s = submission_form.save()
            fields = ('submission_name', 'message', 'UUID')
            return serialize(s, fields)  # Should return a 201 code
        else:
            # TODO: get the error from form and return it here; form.errors()
            return {'error': 'Input information is not correctly formatted'}
