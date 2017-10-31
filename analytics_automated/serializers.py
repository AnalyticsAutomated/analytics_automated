from rest_framework import serializers

from .models import *


class ResultSerializer (serializers.ModelSerializer):
    data_url = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ('task', 'name', 'message', 'step', 'data_url')

    def get_data_url(self, obj):
        return(obj.result_data.name.split("analytics_automated", 1)[1])


class SubmissionInputSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('job', 'email', 'submission_name')


class SubmissionOutputSerializer (serializers.ModelSerializer):
    results = ResultSerializer(many=True)
    state = serializers.CharField(source='returnStatus')

    class Meta:
        model = Submission
        fields = ('submission_name', 'UUID', 'state', 'last_message', 'email',
                  'input_data', 'results')


class JobSerializer (serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('pk', 'name',)
