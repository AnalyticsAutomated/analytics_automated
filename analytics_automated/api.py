from ipware.ip import get_ip

from django import forms

from restless.preparers import FieldsPreparer
from restless.dj import DjangoResource
from restless.exceptions import BadRequest

from .models import Job, Submission


class SubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('submission_name', 'email', 'ip', )


class SubmissionResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'job': 'job.name',
        'submission_name': 'submission_name',
        'UUID': 'UUID',
        'email': 'email',
        'ip': 'ip',
        #'input_data': 'input_data.name',
        'status': 'status',
        'message': 'message',
        'claimed': 'claimed',
        'worker_id': 'worker_id',
    })

    def list(self):
        return Submission.objects.all()

    def is_authenticated(self):
        # Open everything wide!
        # DANGEROUS, DO NOT DO IN PRODUCTION.
        return True

        # Alternatively, if the user is logged into the site...
        # return self.request.user.is_authenticated()

        # Alternatively, you could check an API key. (Need a model for this...)
        # from myapp.models import ApiKey
        # try:
        #     key = ApiKey.objects.get(key=self.request.GET.get('api_key'))
        #     return True
        # except ApiKey.DoesNotExist:
        #     return False

    def create(self):
        self.data['ip'] = get_ip(self.request)
        # I think this validation should be in the form but I'll be buggered
        # if I can work out how to do that
        try:
            self.data['job'] = Job.objects.get(name=self.data['job_name'])
            del self.data['job_name']
        except Exception as e:
            raise BadRequest('Job does not exist')

        form = SubmissionForm(self.data)
        if not form.is_valid():
            raise BadRequest('Input data not valid')
        else:
            return Submission.objects.create(
             job=self.data['job'],
             submission_name=self.data['submission_name'],
             email=self.data['email'],
             ip=self.data['ip'],
             # input_data='input_data.name',
             )

    # GET /api/posts/<pk>/ (but not hooked up yet)
    def detail(self, pk):
        return Submission.objects.get(id=pk)
