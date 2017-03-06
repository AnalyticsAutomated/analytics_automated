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
    Unit tests for the private functions in the api.py files
'''


class CeleryChainConstructionTests(APITestCase):

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

    def test__construct_chain_string(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=True,
                                     rest_alias="this")
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that",
                                     default=123,
                                     spacing=True)
        p1 = ParameterFactory.create(task=self.t, flag="VALUE",
                                     bool_valued=False,
                                     rest_alias="other",
                                     default="huh")

        request_contents = {'task1_this': 'True', 'task1_that': 123,
                            'task1_other': 'things'}
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 1, 'task1', ['-t', '-th'], "
                                    "{'-th': {'spacing': True, "
                                    "'switchless': False, 'value': 123}}, "
                                    "'things', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__ensure_option_order_preserved_with_value(self):
        p1 = ParameterFactory.create(task=self.t, flag="-t", bool_valued=True,
                                     rest_alias="this")
        p1 = ParameterFactory.create(task=self.t, flag="VALUE",
                                     bool_valued=False,
                                     rest_alias="other",
                                     default="huh")
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that",
                                     default=123,
                                     spacing=True)

        request_contents = {'task1_this': 'True', 'task1_that': 123,
                            'task1_other': 'things'}
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 1, 'task1', ['-t', '-th'], "
                                    "{'-th': {'spacing': True, "
                                    "'switchless': False, 'value': 123}}, "
                                    "'things', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__ensure_we_pass_more_than_one_option(self):
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that",
                                     default=123,
                                     spacing=True)
        p1 = ParameterFactory.create(task=self.t, flag="-ch",
                                     bool_valued=False,
                                     rest_alias="chain",
                                     default="CU",
                                     spacing=True)

        request_contents = {'task1_chain': 'AS', 'task1_that': 123, }
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        # print(chain_str)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 1, 'task1', ['-th', '-ch'], "
                                    "{'-ch': {'spacing': True, "
                                    "'switchless': False, 'value': 'AS'}, "
                                    "'-th': {'spacing': True, "
                                    "'switchless': False, 'value': 123}}, "
                                    "'', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__option_uses_default_if_not_passed(self):
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that",
                                     default=123,
                                     spacing=True)

        request_contents = {'task1_chain': 'AS', }
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        # print(chain_str)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 1, 'task1', ['-th'], "
                                    "{'-th': {'spacing': True, "
                                    "'switchless': False, 'value': '123'}}, "
                                    "'', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__request_sets_option_value(self):
        p1 = ParameterFactory.create(task=self.t, flag="-th",
                                     bool_valued=False,
                                     rest_alias="that",
                                     default=123,
                                     spacing=True)

        request_contents = {'task1_that': 456, }
        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 1, 'task1', ['-th'], "
                                    "{'-th': {'spacing': True, "
                                    "'switchless': False, 'value': 456}}, "
                                    "'', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__construct_chain_string_multitask(self):
        self.t2 = TaskFactory.create(backend=self.b, name="task2",
                                     executable="rm")
        s = StepFactory(job=self.j1, task=self.t2, ordering=1)

        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        request_contents = {}
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 2, 'task1', [], "
                                    "{}, '', 1, {}), immutable=True, "
                                    "queue='localhost'), "
                                    "task_runner.subtask(('" + local_id +
                                    "', 1, 2, 2, 2, 'task2', [], "
                                    "{}, '', 1, {}), immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__construct_group_chain_string(self):
        self.t2 = TaskFactory.create(backend=self.b, name="task2",
                                     executable="rm")
        s = StepFactory(job=self.j1, task=self.t2, ordering=1)
        self.t3 = TaskFactory.create(backend=self.b, name="task3",
                                     executable="diff")
        s = StepFactory(job=self.j1, task=self.t3, ordering=1)
        self.t4 = TaskFactory.create(backend=self.b, name="task4",
                                     executable="wc")
        s = StepFactory(job=self.j1, task=self.t4, ordering=2)

        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        request_contents = {}
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 4, 'task1', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost'), "
                                    "group(task_runner.subtask(('" + local_id +
                                    "', 1, 2, 2, 4, 'task2', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost'), "
                                    "task_runner.subtask(('" + local_id +
                                    "', 1, 2, 3, 4, 'task3', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost')), "
                                    "task_runner.subtask(('" + local_id +
                                    "', 2, 3, 4, 4, 'task4', [], {}, '', 1, {}), "
                                    "immutable=True, "
                                    "queue='localhost'),).apply_async()")

    def test__construct_chain_string_with_ending_group(self):
        self.t2 = TaskFactory.create(backend=self.b, name="task2",
                                     executable="rm")
        s = StepFactory(job=self.j1, task=self.t2, ordering=1)
        self.t3 = TaskFactory.create(backend=self.b, name="task3",
                                     executable="diff")
        s = StepFactory(job=self.j1, task=self.t3, ordering=1)

        steps = self.j1.steps.all().select_related('task') \
                       .extra(order_by=['ordering'])
        sd = SubmissionDetails()
        local_id = str(uuid.uuid1())
        request_contents = {}
        chain_str = sd._SubmissionDetails__construct_chain_string(
                    steps, request_contents, local_id, 1)
        # print(chain_str)
        self.assertEqual(chain_str, "chain(task_runner.subtask(('" + local_id +
                                    "', 0, 1, 1, 4, 'task1', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost'), "
                                    "group(task_runner.subtask(('" + local_id +
                                    "', 1, 2, 2, 4, 'task2', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost'), "
                                    "task_runner.subtask(('" + local_id +
                                    "', 1, 2, 3, 4, 'task3', [], {}, '', 1, {}), "
                                    "immutable=True, queue='localhost')), "
                                    "chord_end.subtask(('" + local_id +
                                    "', 2, 4), immutable=True, "
                                    "queue='localhost'),).apply_async()")
