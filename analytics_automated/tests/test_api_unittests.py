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
from django.contrib.auth.models import User

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
    Unit tests for the private functions in the api.py files
'''


class APIPrivateFunctionTests(APITestCase):

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
        user = User.objects.create_user('temporary', 'temporary@gmail.com',
                                        'temporary')
        settings.QUEUE_HOG_SIZE = 10
        settings.QUEUE_HARD_LIMIT = 15

    def tearDown(self):
        clearDatabase()

    def test_get_job_priority_returns_default_priority(self):
        sd = SubmissionDetails()
        priority, value = sd._SubmissionDetails__get_job_priority(False,
                                                                  "127.0.0.1")
        self.assertEquals(priority, settings.DEFAULT_JOB_PRIORITY)
        self.assertEquals(value, 0)

    def test_get_job_priority_returns_low_priority(self):
        for i in range(0, settings.QUEUE_HOG_SIZE):
            s = SubmissionFactory.create(ip="127.0.0.1")
        sd = SubmissionDetails()
        priority, value = sd._SubmissionDetails__get_job_priority(False,
                                                                  "127.0.0.1")
        self.assertEquals(priority, Submission.LOW)
        self.assertEquals(value, 10)

    def test_get_job_priority_returns_none_priority(self):
        for i in range(0, settings.QUEUE_HARD_LIMIT):
            s = SubmissionFactory.create(ip="127.0.0.1")
        sd = SubmissionDetails()
        priority, value = sd._SubmissionDetails__get_job_priority(False,
                                                                  "127.0.0.1")
        self.assertEquals(priority, None)
        self.assertEquals(value, 15)

    # strictly these next 3 should be repeeated for logged in status
    def test_get_job_priority_returns_default_priority_with_unset_limits(self):
        for i in range(0, settings.QUEUE_HARD_LIMIT):
            s = SubmissionFactory.create(ip="127.0.0.1")
        with self.settings(QUEUE_HARD_LIMIT=None), \
                self.settings(QUEUE_HOG_SIZE=None):
            sd = SubmissionDetails()
            priority, value = sd._SubmissionDetails__get_job_priority(
                              False, "127.0.0.1")
            self.assertEquals(priority, settings.DEFAULT_JOB_PRIORITY)
            self.assertEquals(value, 15)

    def test_get_job_priority_returns_low_priority_with_unset_hard_limit(self):
        for i in range(0, settings.QUEUE_HARD_LIMIT):
            s = SubmissionFactory.create(ip="127.0.0.1")
        with self.settings(QUEUE_HARD_LIMIT=None):
            sd = SubmissionDetails()
            priority, value = sd._SubmissionDetails__get_job_priority(
                              False, "127.0.0.1")
            self.assertEquals(priority, settings.DEFAULT_JOB_PRIORITY-1)
            self.assertEquals(value, 15)

    def test_get_job_priority_returns_def_priority_with_unset_hog_size(self):
        for i in range(0, settings.QUEUE_HOG_SIZE):
            s = SubmissionFactory.create(ip="127.0.0.1")
        with self.settings(QUEUE_HOG_SIZE=None):
            sd = SubmissionDetails()
            priority, value = sd._SubmissionDetails__get_job_priority(
                              False, "127.0.0.1")
            self.assertEquals(priority, settings.DEFAULT_JOB_PRIORITY)
            self.assertEquals(value, 10)

    def test_get_job_priority_returns_logged_priority(self):
        self.client.login(username='temporary', password='temporary')
        sd = SubmissionDetails()
        priority, value = sd._SubmissionDetails__get_job_priority(True,
                                                                  "127.0.0.1")
        self.assertEquals(priority, settings.LOGGED_IN_JOB_PRIORITY)
        self.assertEquals(value, 0)

    def test_get_job_priority_returns_logged_lower_priority(self):
        for i in range(0, settings.QUEUE_HOG_SIZE):
            s = SubmissionFactory.create(ip="127.0.0.1")
        self.client.login(username='temporary', password='temporary')
        sd = SubmissionDetails()
        priority, value = sd._SubmissionDetails__get_job_priority(True,
                                                                  "127.0.0.1")
        self.assertEquals(priority, settings.LOGGED_IN_JOB_PRIORITY-1)
        self.assertEquals(value, 10)

    def test_get_job_returns_job_id(self):
        sd = SubmissionDetails()
        value = sd._SubmissionDetails__get_job("job1")
        self.assertEqual(value, [self.j1.pk])

    def test_get_job_raises_if_not_entry(self):
        sd = SubmissionDetails()
        self.assertRaises(Exception, sd._SubmissionDetails__get_job, "argl")

    def test__return_value_returns_value_flag(self):
        p1 = ParameterFactory.create(task=self.t, flag="VALUE",
                                     bool_valued=False,
                                     rest_alias="this")
        sd = SubmissionDetails()
        value = sd._SubmissionDetails__return_value(self.t,
                                                    {'task1_this': 456})
        self.assertEqual(value, 456)

    def test__return_value_default_with_no_value_flag(self):
        p1 = ParameterFactory.create(task=self.t, flag="VALUE",
                                     bool_valued=False,
                                     rest_alias="this",
                                     default="A")
        sd = SubmissionDetails()
        value = sd._SubmissionDetails__return_value(self.t,
                                                    {'task1_that': 456})
        self.assertEqual(value, "A")

    def test__return_value_empty_string_with_no_value_set(self):
        p1 = ParameterFactory.create(task=self.t, flag="thingy",
                                     bool_valued=False,
                                     rest_alias="this")
        sd = SubmissionDetails()
        value = sd._SubmissionDetails__return_value(self.t,
                                                    {'task1_this': 456})
        self.assertEqual(value, '')

    def test__build_environment_returns_valid_dict(self):
        p1 = EnvironmentFactory.create(task=self.t, env="Test", value="McPath")
        sd = SubmissionDetails()
        dict = sd._SubmissionDetails__build_environment(self.t)
        self.assertEqual(dict, {"Test": "McPath"})

    def test__build_environment_returns_empty_dict_without_settings(self):
        sd = SubmissionDetails()
        dict = sd._SubmissionDetails__build_environment(self.t)
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

    def test_params_rejected_with_punctuation(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_this':
                                                          'asd|:'})
        self.assertEqual(bool, False)

    def test_params_reject_with_unix_commands(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_this':
                                                          'rm'})
        self.assertEqual(bool, False)

    def test_params_rejected_with_python_reserved_words(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_this':
                                                          'import'})
        self.assertEqual(bool, False)

    def test_params_rejected_with_r_reserved_words(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=False,
                                     rest_alias="this")
        steps = self.j1.steps.all()
        sd = SubmissionDetails()
        bool = sd._SubmissionDetails__test_params(steps, {'task1_this':
                                                          'format.packageInfo'})
        self.assertEqual(bool, False)

    #
    # TEST FOR __submit_job needed here
    #


    # THIS TEST BROKEN FOR DJANGO REST FRAMEWORK 3.5.x
    #
    # @patch('uuid.uuid1', return_value="f7a314fe-2bda-11e5-bda2-989096c13ee6")
    # def test__prepare_data(self, m):
    #     # request = self.factory.post(reverse('submission'), self.data,
    #     #                             content_type="multipart/form-data")
    #     factory = APIRequestFactory()
    #     request = factory.post(reverse('submission'), self.data,
    #                            content_type="multipart/form-data")
    #     drf_request = Request(request, parsers=(FormParser, MultiPartParser),)
    #     sd = SubmissionDetails()
    #     data, request_data = sd._SubmissionDetails__prepare_data(drf_request)
    #     self.assertEqual(data, {'UUID': "f7a314fe-2bda-11e5-bda2-989096c13ee6",
    #                             'ip': '127.0.0.1', 'email': 'a@b.com',
    #                             'job': 'job1', 'submission_name': 'test'})
