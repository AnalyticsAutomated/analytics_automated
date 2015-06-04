from ipware.ip import get_ip

from restless.preparers import FieldsPreparer
from restless.dj import DjangoResource

from .models import Job, Submission


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
        ip = get_ip(self.request)
        print(ip)
        try:
            this_job = Job.objects.get(name=self.data['job'])
        except Job.DoesNotExist:
            return False

        return Submission.objects.create(
             job=this_job,
             submission_name=self.data['submission_name'],
             email=self.data['email'],
             ip=ip,
             input_data='input_data.name',
        )

    # GET /api/posts/<pk>/ (but not hooked up yet)
    def detail(self, pk):
        return Submission.objects.get(id=pk)
