from rest_framework import serializers

from .models import *


class ResultSerializer (serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('task', 'name', 'message', 'step', 'result_data')


class SubmissionInputSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('job', 'email', 'submission_name')


class SubmissionOutputSerializer (serializers.ModelSerializer):
    results = ResultSerializer(many=True)
    state = serializers.CharField(source='returnStatus')

    class Meta:
        model = Submission
        fields = ('submission_name', 'UUID', 'state', 'last_message',
                  'input_data', 'results')


class JobSerializer (serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('pk', 'name',)
