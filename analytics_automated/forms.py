from django import forms
from .models import Submission, Job


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('job', 'submission_name', 'UUID', 'email', 'ip', 'input_data',)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name',)
