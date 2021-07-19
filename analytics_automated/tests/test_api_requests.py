import json
import io
import uuid
import datetime
import pytz
import glob
from unipath import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.conf import settings
from django.http import HttpRequest
from django.template import RequestContext
from django.urls import reverse
from django.urls import reverse_lazy

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser

from analytics_automated.api import SubmissionDetails
from analytics_automated.models import *
from .model_factories import *
from analytics_automated.tasks import *
from .helper_functions import clearDatabase

'''
    Assorted tests to test the API request responses in the api.py post()
    function
'''

class JobListTests(APITestCase):

    def test_return_of_available_job_types(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")
        response = self.client.get(reverse('job',)+"?format=json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"count":2,"next":null,"previous":null,' \
                    '"results":[{"pk":4,"name":"job1"},{"pk":5'\
                    ',"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        clearDatabase()


class JobDetailTests(APITestCase):

    def test_can_get_multi_step_job_config(self):
        j1 = JobFactory.create(name="job1")
        b = BackendFactory.create(root_path="/tmp/")
        t1 = TaskFactory.create(backend=b, name="task1", executable="ls")
        t2 = TaskFactory.create(backend=b, name="task2", executable="grep")
        s1 = StepFactory(job=j1, task=t1, ordering=0)
        s2 = StepFactory(job=j1, task=t2, ordering=1)
        c1 = ConfigurationFactory(task=t1, name="ls", type=0, parameters='',
                                  version="1")
        c2 = ConfigurationFactory(task=t1, name="dataset", type=1,
                                  parameters='', version="2")
        c3 = ConfigurationFactory(task=t2, name="grep", type=0, parameters='',
                                  version="")
        response = self.client.get(reverse('job',)+"job1?format=json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"name":"job1","steps":[{"task":{"configuration":' \
                    '[{"type":"Dataset","name":"dataset","parameters":' \
                    '"","version":"2"},{"type":"Software","name":' \
                    '"ls","parameters":"","version":"1"}]},"ordering"' \
                    ':0},{"task":{"configuration":[{"type"' \
                    ':"Software","name":"grep","parameters"' \
                    ':"","version":""}]},"ordering":1}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_can_not_get_congif_with_non_existent_job_name(self):
        j1 = JobFactory.create(name="job1")
        b = BackendFactory.create(root_path="/tmp/")
        t1 = TaskFactory.create(backend=b, name="task1", executable="ls")
        t2 = TaskFactory.create(backend=b, name="task2", executable="grep")
        s1 = StepFactory(job=j1, task=t1, ordering=0)
        s2 = StepFactory(job=j1, task=t2, ordering=1)
        c1 = ConfigurationFactory(task=t1, name="ls", type=1, parameters='',
                                  version="1")
        c2 = ConfigurationFactory(task=t1, name="dataset", type=2,
                                  parameters='', version="2")
        c3 = ConfigurationFactory(task=t2, name="grep", type=2, parameters='',
                                  version="")
        response = self.client.get(reverse('job',)+"job2?format=json")
        response.render()
        self.assertEqual(response.status_code, 404)
        test_data = '{"detail":"Not found."}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        clearDatabase()


class JobTimeTests(APITestCase):

    def test_return_times_when_available(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")

        this_s1 = SubmissionFactory.create(job=j1, status=Submission.COMPLETE)
        start1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=15, second=0, tzinfo=pytz.UTC)
        stop1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s1.pk).update(created=start1,
                                                        modified=stop1)
        this_s2 = SubmissionFactory.create(job=j1, status=Submission.COMPLETE)
        start2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=40, second=0, tzinfo=pytz.UTC)
        stop2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s2.pk).update(created=start2,
                                                        modified=stop2)
        this_s3 = SubmissionFactory.create(job=j2, status=Submission.COMPLETE)
        start3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=5, second=0, tzinfo=pytz.UTC)
        stop3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=50, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s3.pk).update(created=start3,
                                                        modified=stop3)
        response = self.client.get(reverse('jobtimes',)+"?format=json")
        self.assertEqual(response.status_code, 200)
        test_data = '{"job2":2700,"job1":1049}'
        test_data_alt = '{"job1":1049,"job2":2700}'
        # either of these return strings is valid. Should possibly force
        # a return order in the API
        try:
            de_datestamp(response.content.decode("utf-8"),test_data)
            self.assertEqual(response.content.decode("utf-8"), test_data)
        except Exception as e:
            self.assertEqual(response.content.decode("utf-8"), test_data_alt)

    def test_return_nothing_where_no_jobs_run(self):
        response = self.client.get(reverse('jobtimes',)+"?format=json")
        self.assertEqual(response.status_code, 200)
        test_data = '{}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_correctly_handle_missing_job(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")

        this_s1 = SubmissionFactory.create(job=j1, status=Submission.COMPLETE)
        start1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=15, second=0, tzinfo=pytz.UTC)
        stop1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s1.pk).update(created=start1,
                                                        modified=stop1)
        this_s2 = SubmissionFactory.create(job=j1, status=Submission.COMPLETE)
        start2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=40, second=0, tzinfo=pytz.UTC)
        stop2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s2.pk).update(created=start2,
                                                        modified=stop2)
        this_s3 = SubmissionFactory.create(job=j2, status=Submission.COMPLETE)
        start3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=5, second=0, tzinfo=pytz.UTC)
        stop3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=50, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s3.pk).update(created=start3,
                                                        modified=stop3)
        j1.delete()
        response = self.client.get(reverse('jobtimes',)+"?format=json")
        self.assertEqual(response.status_code, 200)
        test_data = '{"job2":2700}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        clearDatabase()


class EndpointListTests(APITestCase):

    def test_return_of_available_endpoint_types(self):
        j1 = JobFactory.create(name="job1")
        b = BackendFactory.create(root_path="/tmp/")
        t1 = TaskFactory.create(backend=b, name="task1", executable="ls")
        p1 = ParameterFactory.create(task=t1, rest_alias="this",
                                     bool_valued=True)
        t2 = TaskFactory.create(backend=b, name="task2",
                                executable="grep")
        p2 = ParameterFactory.create(task=t2, rest_alias="that")
        s1 = StepFactory(job=j1, task=t1, ordering=0)
        s2 = StepFactory(job=j1, task=t2, ordering=1)

        response = self.client.get(reverse('endpoints',)+"?format=json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"jobs":["/submission/&job=job1&' + \
                    'submission_name=[STRING]&email=[EMAIL_STRING]&' + \
                    'input_data=[FILE]&task1_this=[TRUE/FALSE]&' + \
                    'task2_that=[TRUE/FALSE]"]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        clearDatabase()


class SubmissionRequestTests(APITestCase):

    file = ''
    data = {}
    factory = APIRequestFactory()
    j1 = None
    j2 = None
    t = None
    t2 = None
    b = None

    def setUp(self):
        self.file = SimpleUploadedFile('file1.txt',
                                       bytes('these are the file contents!',
                                             'utf-8'))
        self.data = {'input_data': self.file,
                     'job': 'job1',
                     'submission_name': 'test',
                     'email': 'a@b.com'}
        self.j1 = JobFactory.create(name="job1")
        self.j2 = JobFactory.create(name="job2")
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="task1",
                                    executable="ls")
        self.t2 = TaskFactory.create(backend=self.b, name="task2",
                                     executable="wc")
        s = StepFactory(job=self.j1, task=self.t, ordering=0)
        s2 = StepFactory(job=self.j2, task=self.t2, ordering=0)
        settings.QUEUE_HOG_SIZE = 10
        settings.QUEUE_HARD_LIMIT = 15

    def tearDown(self):
        clearDatabase()

    def test_submission_detail_is_returned(self,):
        s1 = SubmissionFactory.create(input_data="test.txt", status=0,
                                      job=self.j1)
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"submission_name":"{0}","job_name":"{1}",' \
                    '"UUID":"{2}"' \
                    ',"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,' \
                    '"input_file":"/submissions/test.txt",' \
                    '"results":[]}}'.format(s1.submission_name,
                                            self.j1.name,
                                            s1.UUID)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_submission_with_results_is_returned(self,):
        s1 = SubmissionFactory.create(input_data="test.txt", status=0,
                                      job=self.j1)
        t1 = TaskFactory.create(name='task1')
        r1 = ResultFactory.create(submission=s1,
                                  task=t1,
                                  name='test',
                                  message='a result',
                                  step=1,
                                  result_data=self.file,)
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"submission_name":"{0}","job_name":"{1}",' \
                    '"UUID":"{2}"' \
                    ',"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,' \
                    '"input_file":"/submissions/test.txt",' \
                    '"results":[{{"task":{3},' \
                    '"name":"{4}","message":"{5}","step":{6},' \
                    '"data_path":"{7}"}}]}}'.format(s1.submission_name,
                                                    self.j1.name,
                                                    s1.UUID, t1.pk, 'test',
                                                    r1.message, r1.step,
                                                    r1.result_data.url)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_batch_with_results_is_returned(self,):
        b1 = BatchFactory.create(status=0)
        s1 = SubmissionFactory.create(input_data="test.txt", status=0,
                                      batch=b1, job=self.j1)
        t1 = TaskFactory.create(name='task1')
        r1 = ResultFactory.create(submission=s1,
                                  task=t1,
                                  name='test',
                                  message='a result',
                                  step=1,
                                  result_data=self.file,)
        response = self.client.get(reverse('batchDetail',
                                           args=[b1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"UUID":"{0}",' \
                    '"state":"Submitted",' \
                    '"submissions":[{{"submission_name":"{1}",' \
                    '"job_name":"{2}",' \
                    '"UUID":"{3}",' \
                    '"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,"input_file":"/submissions/test.txt",' \
                    '"results":[{{"task":{4},"name":"{5}",' \
                    '"message":"{6}","step":{7},' \
                    '"data_path":"{8}"}}]}}]}}'.format(b1.UUID,
                                                       s1.submission_name,
                                                       self.j1,
                                                       s1.UUID, t1.pk, 'test',
                                                       r1.message, r1.step,
                                                       r1.result_data.url)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_batch_with_multiple_submissions_results_are_returned(self,):
        b1 = BatchFactory.create(status=0)
        s1 = SubmissionFactory.create(input_data="test.txt", status=0,
                                      batch=b1, job=self.j1)
        t1 = TaskFactory.create(name='task1')
        r1 = ResultFactory.create(submission=s1,
                                  task=t1,
                                  name='test',
                                  message='a result',
                                  step=1,
                                  result_data=self.file,)
        s2 = SubmissionFactory.create(input_data="test.txt", status=0,
                                      batch=b1, job=self.j2)
        t2 = TaskFactory.create(name='task2')
        r2 = ResultFactory.create(submission=s2,
                                  task=t2,
                                  name='test',
                                  message='a result',
                                  step=1,
                                  result_data=self.file,)
        response = self.client.get(reverse('batchDetail',
                                           args=[b1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"UUID":"{0}",' \
                    '"state":"Submitted",' \
                    '"submissions":[{{"submission_name":"{1}",' \
                    '"job_name":"{2}",' \
                    '"UUID":"{3}",' \
                    '"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,"input_file":"/submissions/test.txt",' \
                    '"results":[{{"task":{4},"name":"{5}",' \
                    '"message":"{6}","step":{7},' \
                    '"data_path":"{8}"}}]}},' \
                    '{{"submission_name":"{9}",' \
                    '"job_name":"{10}",' \
                    '"UUID":"{11}",' \
                    '"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,"input_file":"/submissions/test.txt",' \
                    '"results":[{{"task":{12},"name":"{13}",' \
                    '"message":"{14}","step":{15},' \
                    '"data_path":"{16}"}}]}}]}}'.format(
                     b1.UUID,
                     s2.submission_name,
                     self.j2,
                     s2.UUID, t2.pk, 'test',
                     r2.message, r2.step,
                     r2.result_data.url,
                     s1.submission_name,
                     self.j1,
                     s1.UUID, t1.pk, 'test',
                     r1.message, r1.step,
                     r1.result_data.url,
                     )
        self.assertEqual(response.content.decode("utf-8"), test_data)

    @patch('builtins.exec', return_value=True)
    def test_submission_accepts_when_file_validates(self, m):
        vt = ValidatorTypesFactory.create(name='png')
        v = ValidatorFactory.create(job=self.j1, validation_type=vt)
        f = open("submissions/files/test.png", "rb").read()
        pngFile = SimpleUploadedFile('test.png', f)
        this_data = {'input_data': pngFile,
                     'job': 'job1',
                     'submission_name': 'test',
                     'email': 'a@b.com'}
        request = self.factory.post(reverse('submission'), this_data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_submission_rejects_when_file_does_not_validate(self, m):
        vt = ValidatorTypesFactory.create(name='png')
        v = ValidatorFactory.create(job=self.j1, validation_type=vt)
        f = open("submissions/files/test.gif", "rb").read()
        pngFile = SimpleUploadedFile('test.gif', f)
        this_data = {'input_data': pngFile,
                     'job': 'job1',
                     'submission_name': 'test',
                     'email': 'a@b.com'}
        request = self.factory.post(reverse('submission'), this_data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('builtins.exec', return_value=True)
    def test_submission_accepts_when_all_params_given(self, m):
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        p2 = ParameterFactory.create(task=self.t, rest_alias="that")
        self.data['task1_this'] = "Value1"
        self.data['task1_that'] = "Value2"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_submission_rejects_when_a_param_is_missed(self, m):
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        p2 = ParameterFactory.create(task=self.t, rest_alias="that")
        self.data['task1_this'] = "Value1"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Submission.objects.all()), 0)

    @patch('builtins.exec', return_value=True)
    def test_submission_ignores_undefined_params(self, m):
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        self.data['task1_strange'] = "Value2"
        self.data['task1_this'] = "Value1"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_submission_checks_params_across_more_than_one_task(self, m):
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        t2 = TaskFactory.create(backend=self.b, name="task2", executable="ls")
        p2 = ParameterFactory.create(task=t2, rest_alias="this2")
        self.data['task2_this2'] = "Value2"
        self.data['task1_this'] = "Value1"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_valid_submission_post_creates_entry(self, m):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_valid_submission_gets_medium_priority(self, m):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        subs = Submission.objects.get()
        self.assertEqual(subs.priority, Submission.MEDIUM)

    @patch('builtins.exec', return_value=True)
    def test_submissions_after_threshold_get_low_priority(self, m):
        for i in range(0, settings.QUEUE_HOG_SIZE):
            s = SubmissionFactory.create(ip="127.0.0.1", status=0)
        # for 'reasons' reverse does not work in this class/test?????
        # request = self.factory.post(reverse('submission'), self.data,
        #                             format='multipart')
        request = self.factory.post('/analytics_automated/submission/',
                                    self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        subs = Submission.objects.all()
        self.assertEqual(subs[10].priority, Submission.LOW)

    @patch('builtins.exec', return_value=True)
    def test_submissions_after_hard_limit_get_rejection(self, m):
        for i in range(0, settings.QUEUE_HARD_LIMIT):
            s = SubmissionFactory.create(ip="127.0.0.1", status=0)
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code,
                         status.HTTP_429_TOO_MANY_REQUESTS)

    def test_rejection_with_bad_email(self):
        self.data['email'] = 'b'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_with_bad_job_id(self):
        self.data['job'] = 'job34'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_with_blank_submission_name(self):
        self.data['submission_name'] = ""
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_submission_name(self):
        del(self.data['submission_name'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_email(self):
        del(self.data['email'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_job(self):
        del(self.data['job'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_input_data(self):
        del(self.data['input_data'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_with_disabled_job(self):
        j3 = JobFactory.create(name="job303", runnable=False)
        b3 = BackendFactory.create(root_path="/tmp/")
        t3 = TaskFactory.create(backend=b3, name="task1",
                                executable="ls")
        s3 = StepFactory(job=j3, task=t3, ordering=0)
        self.data['job'] = 'job303'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Batch processing tests
    @patch('builtins.exec', return_value=True)
    def test_submission_makes_single_batch_entry(self, m):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Batch.objects.all()), 1)

    @patch('builtins.exec', return_value=True)
    def test_dual_submission_makes_common_batch_entries(self, m):
        self.data['job'] = 'job1,job2'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        batch_entries = Batch.objects.all()
        submission_entries = Submission.objects.all()
        self.assertEqual(len(batch_entries), 1)
        self.assertEqual(len(submission_entries), 2)
        self.assertEqual(submission_entries[0].batch, batch_entries[0])
        self.assertEqual(submission_entries[1].batch, batch_entries[0])

    @patch('builtins.exec', return_value=True)
    def test_multiple_submission_makes_seperate_batch_entries(self, m):
        self.data['job'] = 'job1'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.data['job'] = 'job2'
        self.data['input_data'] = SimpleUploadedFile('file1.txt',
                                                     bytes('these are the '
                                                           'file contents!',
                                                           'utf-8'))
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        batch_entries = Batch.objects.all()
        self.assertEqual(len(batch_entries), 2)
        self.assertNotEqual(batch_entries[0].UUID, batch_entries[1].UUID)

    @patch('builtins.exec', return_value=True)
    def test_reject_where_one_job_does_not_exist(self, m):
        self.data['job'] = 'job1,job34'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        batch_entries = Batch.objects.all()
        self.assertEqual(len(batch_entries), 0)
        self.assertEqual(len(Submission.objects.all()), 0)

    @patch('builtins.exec', return_value=True)
    def test_accept_batch_with_params(self, m):
        self.data['job'] = 'job1,job2'
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        p2 = ParameterFactory.create(task=self.t2, rest_alias="that")
        self.data['task1_this'] = "Value1"
        self.data['task2_that'] = "Value2"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('builtins.exec', return_value=True)
    def test_reject_batch_with_missin_params(self, m):
        self.data['job'] = 'job1,job2'
        p1 = ParameterFactory.create(task=self.t, rest_alias="this")
        p2 = ParameterFactory.create(task=self.t2, rest_alias="that")
        self.data['task1_this'] = "Value1"
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
