from rest_framework import serializers

from .models import Job, Submission


class SubmissionInputSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('job', 'email', 'submission_name')
        

class SubmissionOutputSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('submission_name', 'UUID')


class JobSerializer (serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('pk', 'name',)
