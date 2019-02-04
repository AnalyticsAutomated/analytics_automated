import uuid
import glob
import os
import factory

from unittest.mock import patch

from commandRunner.localRunner import *

from django.db import transaction
from django.test import TestCase

from django.test import override_settings

from analytics_automated.tasks import *
from analytics_automated import tasks
from analytics_automated.models import Submission, Message
from .model_factories import *
from .helper_functions import clearDatabase

'''
    Unit tests for private functions in the task.py class
'''


class TaskPrivateFunctionUnitTests(TestCase):
    uuid1 = ""
    b = None
    t = None
    j = None
    s = None
    batch = None
    sub = None
    messages = None

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    def testTrivialAdd(self):
        """
            Here we test that our task_runner function does it's thing
        """
        result = add.delay(8, 8)
        self.assertEquals(result.get(), 16)
        self.assertTrue(result.successful())

    def setUp(self):
        step_value = random.randint(1, 20)
        self.uuid1 = str(uuid.uuid1())
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="test_task",
                                    executable="grep 'previous' /tmp/",
                                    in_glob="txt", out_glob="out")
        self.j = JobFactory.create()
        self.s = StepFactory(job=self.j, task=self.t, ordering=0)
        self.batch = BatchFactory.create()
        self.sub = SubmissionFactory.create(UUID=self.uuid1, job=self.j,
                                            batch=self.batch)

    def tearDown(self):
        clearDatabase()

    def test_get_data_correctly_gets_input_data(self):
        data, previous_step = tasks.get_data(self.sub, self.sub.UUID, 1,
                                             [".txt", ])
        self.assertEqual(data, {self.sub.UUID+".txt": "these are the file "
                                                      "contents!\n"})

    def test_get_data_correctly_gets_previous_data(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 2,
                                             [".txt"])
        self.assertEqual(data, {res.result_data.name: "Here is some previous "
                                                      "results!\n"})

    def test_correctly_gets_multiple_prior_results(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        res2 = ResultFactory.create(submission=self.sub,
                                    task=self.t,
                                    step=1,
                                    previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 2,
                                             [".txt"])
        self.assertEqual(data,
                         {res2.result_data.name: "Here is some previous "
                                                 "results!\n",
                          res.result_data.name: "Here is some previous "
                                                "results!\n"
                          })

    def test_correctly_gets_multiple_results_from_multiple_prior_steps(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        res2 = ResultFactory.create(submission=self.sub,
                                    task=self.t,
                                    step=2,
                                    previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 3,
                                             [".txt"])
        self.assertEqual(data,
                         {res2.result_data.name: "Here is some previous "
                                                 "results!\n",
                          res.result_data.name: "Here is some previous "
                                                "results!\n"
                          })

    def test_correctly_gets_2_different_results_from_multiple_prior_steps(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        RESULT_DATA = settings.BASE_DIR.child("submissions").child("files"). \
                                                             child("result1.txt2")
        res2 = ResultFactory.create(submission=self.sub,
                                    task=self.t,
                                    step=2,
                                    previous_step=None,
                                    result_data = factory.django.FileField(from_path=RESULT_DATA),)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 3,
                                             [".txt", ".txt2"])
        self.assertEqual(data,
                         {res2.result_data.name: "Here is some previous "
                                                 "results!\n",
                          res.result_data.name: "Here is some previous "
                                                "results!\n"
                          })


    def test_only_gets_previous_data_when_there_is_an_inglobs_match(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 2,
                                             [".csv"])
        self.assertEqual(data, {})
