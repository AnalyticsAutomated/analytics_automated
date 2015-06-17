from rest_framework import serializers

from .models import Job, Submission


class SubmissionSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('pk', 'job', 'ip', 'email', 'submission_name', 'UUID')


class JobSerializer (serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('pk', 'name',)
