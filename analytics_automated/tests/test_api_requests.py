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
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy

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
    Assorted tests to test the API request responses in the apy.py post()
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
                    '"results":[{"pk":2,"name":"job1"},{"pk":3'\
                    ',"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        clearDatabase()


class JobTimeTests(APITestCase):

    def test_return_times_when_available(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")

        this_s1 = SubmissionFactory.create(job=j1)
        start1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=15, second=0, tzinfo=pytz.UTC)
        stop1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s1.pk).update(created=start1,
                                                        modified=stop1)
        this_s2 = SubmissionFactory.create(job=j1)
        start2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=40, second=0, tzinfo=pytz.UTC)
        stop2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s2.pk).update(created=start2,
                                                        modified=stop2)
        this_s3 = SubmissionFactory.create(job=j2)
        start3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=5, second=0, tzinfo=pytz.UTC)
        stop3 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=50, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s3.pk).update(created=start3,
                                                        modified=stop3)
        response = self.client.get(reverse('jobtimes',)+"?format=json")
        self.assertEqual(response.status_code, 200)
        test_data = '{"job2":2700,"job1":1050}'
        test_data_alt = '{"job1":1050,"job2":2700}'
        # either of these return strings is valid. Should possibly force
        # a return order in the API
        try:
            self.assertEqual(response.content.decode("utf-8"), test_data)
        except:
            self.assertEqual(response.content.decode("utf-8"), test_data_alt)

    def test_return_nothing_where_no_jobs_run(self):
        response = self.client.get(reverse('jobtimes',)+"?format=json")
        self.assertEqual(response.status_code, 200)
        test_data = '{}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_correctly_handle_missing_job(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")

        this_s1 = SubmissionFactory.create(job=j1)
        start1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=15, second=0, tzinfo=pytz.UTC)
        stop1 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s1.pk).update(created=start1,
                                                        modified=stop1)
        this_s2 = SubmissionFactory.create(job=j1)
        start2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                   minute=40, second=0, tzinfo=pytz.UTC)
        stop2 = datetime.datetime(year=2016, month=3, day=21, hour=12,
                                  minute=45, second=0, tzinfo=pytz.UTC)
        Submission.objects.filter(pk=this_s2.pk).update(created=start2,
                                                        modified=stop2)
        this_s3 = SubmissionFactory.create(job=j2)
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
    t = None
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
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="task1",
                                    executable="ls")
        s = StepFactory(job=self.j1, task=self.t, ordering=0)

    def tearDown(self):
        clearDatabase()

    def test_submission_detail_is_returned(self,):
        s1 = SubmissionFactory.create(input_data="test.txt")
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"submission_name":"submission_0","UUID":"{0}"' \
                    ',"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,' \
                    '"input_file":"/submissions/test.txt",' \
                    '"results":[]}}'.format(s1.UUID)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_submission_with_results_is_returned(self,):
        s1 = SubmissionFactory.create(input_data="test.txt")
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
        test_data = '{{"submission_name":"{0}","UUID":"{1}"' \
                    ',"state":"Submitted","last_message":"Submitted",' \
                    '"email":null,' \
                    '"input_file":"/submissions/test.txt",' \
                    '"results":[{{"task":{2},' \
                    '"name":"{3}","message":"{4}","step":{5},' \
                    '"data_path":"{6}"}}]}}'.format(s1.submission_name,
                                                    s1.UUID, t1.pk, 'test',
                                                    r1.message, r1.step,
                                                    r1.result_data.url)
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
            s = SubmissionFactory.create(ip="127.0.0.1")
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
            s = SubmissionFactory.create(ip="127.0.0.1")
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
