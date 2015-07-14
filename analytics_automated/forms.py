import re
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Submission, Job, Validator


class SubmissionForm(forms.ModelForm):

    def clean_input_data(self):
        input_data = self.cleaned_data.get("input_data")
        job = self.cleaned_data.get("job")
        j = Job.objects.get(name=job)
        v = j.validators.all()
        if len(v) == 0:  # Nothing to do here
            return(input_data)
        match_state = False
        for validator in v:
            if validator.validation_type == Validator.REGEX:
                is_valid = False
                data = input_data.read().decode(encoding='UTF-8')
                regex = re.compile(validator.re_string)
                if regex.match(data):
                    match_state = True
                else:
                    raise forms.ValidationError("Input Data does not match "
                                                "custom REGEX validation")
            if validator.validation_type == Validator.MP3:
                raise NotImplementedError
            if validator.validation_type == Validator.IMAGE:
                raise NotImplementedError

        if match_state is False:
            raise forms.ValidationError("Input Data could not pass custom validation")
        else:
            return(input_data)

    class Meta:
        model = Submission
        fields = ('job', 'submission_name', 'UUID', 'email',
                  'ip', 'input_data',)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name',)


class ValidatorForm(BaseInlineFormSet):

    class Meta:
        model = Validator
