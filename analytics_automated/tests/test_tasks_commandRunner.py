import uuid
import glob
import os

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
    Test the task interaction with the commandRunner module
'''

class TaskTestCase(TestCase):
    uuid1 = ""
    b = None
    t = None
    j = None
    s = None
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
        self.sub = SubmissionFactory.create(UUID=self.uuid1, job=self.j)

    def tearDown(self):
        clearDatabase()

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerSuccess(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 1, "test_task", [], {}, None,
                          1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        # print(self.sub)
        self.assertEqual(self.sub.last_message, "Completed job at step #1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerAllMessagesSent(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 1, "test_task", [], {}, None,
                          1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.messages = Message.objects.all().filter(submission=self.sub)
        # for m in self.messages:
        #     print(str(m))
        self.assertGreater(len(self.messages), 1)

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=1)
    def testTaskRunnerExecuteNoneZeroExit(self, m):
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 1, 1, 1,
                          "test_task", [], {}, None, 1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Failed step, non 0 exit at "
                                                "step: 0. Exit status:1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerSignalsRunningWhenNotAtLastStep(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_task", [], {}, None,
                          1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Completed step: 1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerDoesGetResultFromPreviousRun(self, m):
        '''
            this tests that it got the previous results correctly. It can only
            write the correct new result entry if it did so
        '''
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        task_runner.delay(self.uuid1, 0, 2, 2, 2, "test_task", [], {}, None,
                          1, {})
        result = Result.objects.get(submission=self.sub, step=2)
        self.assertEqual(result.message, "Result")
