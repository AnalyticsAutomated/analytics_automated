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


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name',)


class ValidatorForm(BaseInlineFormSet):

    class Meta:
        model = Validator

    '''
       Validate formset data here
    '''
    def clean(self):
        re_string = ''
        validation_type = ''
        for formset in self.cleaned_data:
            re_string = formset['re_string']
            validation_type = formset['validation_type']
            if validation_type == Validator.REGEX:
                is_valid = False
                try:
                    re.compile(re_string)
                    is_valid = True
                except re.error:
                    is_valid = False
                if is_valid is False:
                    raise(ValidationError("REGULAR EXPRESSION IS NOT VALID: " +
                                          re_string))
