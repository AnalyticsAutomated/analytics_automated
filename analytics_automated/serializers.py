from rest_framework import serializers

from .models import *


class ConfigurationSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='returnType')

    class Meta:
        model = Configuration
        fields = ('type', 'name', 'parameters', 'version')


class TaskSerializer(serializers.ModelSerializer):
    configuration = ConfigurationSerializer(many=True, allow_null=True)

    class Meta:
        model = Task
        fields = ('configuration', )


class StepSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = Step
        fields = ('task', 'ordering')


class JobDetailSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, allow_null=True)

    class Meta:
        model = Job
        fields = ('name', 'steps')


class ResultSerializer (serializers.ModelSerializer):
    data_path = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ('task', 'name', 'message', 'step', 'data_path')

    def get_data_path(self, obj):
        try:
            return(obj.result_data.url.split("analytics_automated", 1)[1])
        except Exception as e:
            return(obj.result_data.url)


class SubmissionOutputSerializer (serializers.ModelSerializer):
    results = ResultSerializer(many=True, allow_null=True)
    state = serializers.CharField(source='returnStatus')
    input_file = serializers.SerializerMethodField()
    job_name = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ('submission_name', 'job_name', 'UUID', 'state',
                  'last_message', 'email', 'input_file', 'results')
        # removed modified from this

    def get_input_file(self, obj):
        try:
            return(obj.input_data.url.split("analytics_automated", 1)[1])
        except Exception as e:
            return(obj.input_data.url)

    def get_job_name(self, obj):
        return(obj.job.name)


class SubmissionInputSerializer (serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('job', 'email', 'submission_name')


class BatchSerializer (serializers.ModelSerializer):
    submissions = SubmissionOutputSerializer(many=True, allow_null=True)
    state = serializers.CharField(source='returnStatus')

    class Meta:
        model = Batch
        fields = ('UUID', 'state', 'submissions')


class JobSerializer (serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('pk', 'name',)
