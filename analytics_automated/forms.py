import re
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Submission, Job, Validator


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('job', 'submission_name', 'UUID', 'email',
                  'ip', 'input_data',)

        def clean_input_data(self):
            pass


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name',)


class ValidatorForm(BaseInlineFormSet):

    class Meta:
        model = Validator
