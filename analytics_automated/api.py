import json
from ipware.ip import get_ip

from django import forms
from django.http import HttpResponse
from django.core import serializers

from restless.views import Endpoint
from restless.modelviews import ListEndpoint, DetailEndpoint


from .models import Job, Submission


class SubmissionList(ListEndpoint):
    model = Submission


class SubmissionDetail(DetailEndpoint):
    model = Submission


class SubmissionData(Endpoint):

    def post(self, request):
        print("Hi")
        return {'message': 'Hello'}
