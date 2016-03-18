import json
import io
import uuid
from unipath import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from .api import SubmissionDetails
from .models import *
from .model_factories import *
from .tasks import *


class JobListTests(APITestCase):

    def test_return_of_available_job_types(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")
        response = self.client.get(reverse('job',)+".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"count":2,"next":null,"previous":null,' \
                    '"results":[{"pk":2,"name":"job1"},{"pk":3'\
                    ',"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()

class JobTimeTests(APITestCase):

    def test_return_time_when_available(self):
        response = self.client.get(reverse('jobtime',
                                           args=["hello", ]))
        self.assertEqual(response.status_code, 200)

    def test_return_nothing_where_no_jobs_run(self):
        pass

    def test_return_undef_if_job_type_does_not_exists(self):
        pass

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()

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
        response = self.client.get(reverse('endpoints',)+".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"jobs":["/submission/&job=job1&' + \
                    'submission_name=[STRING]&email=[EMAIL_STRING]&' + \
                    'input_data=[FILE]&task1_this=[TRUE/FALSE]&' + \
                    'task2_that=[TRUE/FALSE]"]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class SubmissionDetailTests(APITestCase):

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
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()

    def test_submission_detail_is_returned(self,):
        s1 = SubmissionFactory.create()
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{{"submission_name":"submission_0","UUID":"{0}"' \
                    ',"state":"Submitted","last_message":"Submitted",' \
                    '"input_data":"http://testserver/submissions/file1_yrgE0W9.txt",' \
                    '"results":[]}}'.format(s1.UUID)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_submission_with_results_is_returned(self,):
        s1 = SubmissionFactory.create()
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
                    '"results":[{{"task":{2},' \
                    '"name":"{3}","message":"{4}","step":{5},' \
                    '"result_data":"{6}"}}]}}'.format(s1.submission_name,
                                                      s1.UUID, t1.pk, 'test',
                                                      r1.message, r1.step,
                                                      "http://testserver" +
                                                      r1.result_data.url)
        self.assertEqual(response.content.decode("utf-8"), test_data)

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
        request = self.factory.post(reverse('submission'), self.data,
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
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

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

    def test_validator_rejection_without_valid_input_data(self):
        null_file = SimpleUploadedFile('file1.txt',
                                       bytes('',
                                             'utf-8'))
        self.data['input_data'] = null_file
        validator = ValidatorFactory(job=self.j1, validation_type=0,
                                     re_string=".+")
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('builtins.exec', return_value=True)
    def test_validator_passes_with_valid_input_data(self, m):
        validator = ValidatorFactory(job=self.j1, validation_type=0,
                                     re_string=".+")
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test__build_flags_returns_valid_array(self):
        p1 = ParameterFactory.create(task=self.t, flag="t", bool_valued=True,
                                     rest_alias="this")
        sd = SubmissionDetails()
        array = sd._SubmissionDetails__build_flags(self.t,
                                                   {'task1_this': 'True'})
        self.assertEqual(array, ["t"])

    def test__build_flags_returns_nothing_flag_set_to_false(self):
        p1 = ParameterFactory.create(task=self.t, flag="t", bool_valued=True,
                                     rest_alias="this")
        sd = SubmissionDetails()
        array = sd._SubmissionDetails__build_flags(self.t,
                                                   {'task1_this': 'False'})
        self.assertEqual(array, [])

    def test__build_flags_returns_nothing_with_mismatch(self):
        p1 = ParameterFactory.create(task=self.t, flag="t", bool_valued=True,
                                     rest_alias="this")
        sd = SubmissionDetails()
        array = sd._SubmissionDetails__build_flags(self.t,
                                                   {'task1_that': 'False'})
        self.assertEqual(array, [])

    def test__build_options_returns_valid_dict(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        sd = SubmissionDetails()
        dict = sd._SubmissionDetails__build_options(self.t,
                                                    {'task1_this': 123})
        self.assertEqual(dict, {"-t": 123})

    def test__build_options_returns_nothing_with_mismatch(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        sd = SubmissionDetails()
        dict = sd._SubmissionDetails__build_options(self.t,
                                                    {'task1_that': 123})
        self.assertEqual(dict, {})

    def test__test_params_returns_true_when_set_is_contained(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_that': 123,
                                                          'task1_this': 69})
        self.assertEqual(bool, True)

    def test__test_params_returns_false_when_set_is_not_complete(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_that': 123, })
        self.assertEqual(bool, False)

    def test__test_params_returns_true_when_too_many_items_passed(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_that': 123,
                                                          'task1_this': 69})
        self.assertEqual(bool, True)

    def test__test_params_returns_true_with_nothing(self):
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {})
        self.assertEqual(bool, True)

    @patch('uuid.uuid1', return_value="f7a314fe-2bda-11e5-bda2-989096c13ee6")
    def test__prepare_data(self, m):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        drf_request = Request(request)
        sd = SubmissionDetails()
        data, request_data = sd._SubmissionDetails__prepare_data(drf_request)
        self.assertEqual(data, {'UUID': "f7a314fe-2bda-11e5-bda2-989096c13ee6",
                                'ip': '127.0.0.1', 'email': 'a@b.com',
                                'job': 'job1', 'submission_name': 'test'})

    def test__construct_chain_string(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=True,
                                     rest_alias="this")
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that")
        request_contents = {'task1_this': 'True', 'task1_that': 123}
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(steps,
                    request_contents,
                    local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 'task1', ['-t'], "
                                    "{'-th': 123}), immutable=True, "
                                    "queue='localhost'))()")
