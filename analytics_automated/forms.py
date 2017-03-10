import re
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Submission, Job, Validator, Task
from .validators import *


class SubmissionForm(forms.ModelForm):

    def __validate_input(self, validators, file_data):
        input_file_contents = file_data.read()
        for validator in validators:
            if not eval(validator.validation_type.name+"(input_file_contents)"):
                return(False)
        return(True)

    def clean_input_data(self):
        input_data = self.cleaned_data.get("input_data")
        job = self.cleaned_data.get("job")
        validators = job.validators.all()
        if len(validators) == 0:  # Nothing to do here
            return(input_data)
        match_state = False
        if not self.__validate_input(validators, input_data):
            raise forms.ValidationError("Input data could not be validated")
        return(input_data)

    class Meta:
        model = Submission
        fields = ('job', 'submission_name', 'UUID', 'email',
                  'ip', 'input_data',)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name',)


class TaskForm(forms.ModelForm):
    executable = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Task
        fields = ('backend', 'name', 'description', 'in_glob', 'out_glob',
                  'stdout_glob', 'executable', 'incomplete_outputs_behaviour',
                  'custom_exit_status', 'custom_exit_behaviour', )


class ValidatorForm(BaseInlineFormSet):

    class Meta:
        model = Validator
