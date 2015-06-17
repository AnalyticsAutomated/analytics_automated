from rest_framework import serializers

from .models import Job, Submission


class SubmissionSerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('job', 'ip', 'email', 'submission_name')


class JobSerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('name')
