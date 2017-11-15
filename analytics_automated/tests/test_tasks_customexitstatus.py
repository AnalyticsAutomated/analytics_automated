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
    Tests cover task's response to different exit behaviours set by the user
'''

class TaskCustomExitBehaviours(TestCase):
    uuid1 = ""
    b = None
    t = None
    j = None
    s = None
    sub = None
    batch = None
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

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=123)
    def testCustomExitContinues(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123",
                                custom_exit_behaviour=Task.CONTINUE)
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_custom_continue", [],
                          {}, None, 1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Completed step: 1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=123)
    def testCustomExitTakesMultipleValues123(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123,500",
                                custom_exit_behaviour=Task.CONTINUE)
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_custom_continue", [],
                          {}, None, 1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Completed step: 1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=500)
    def testCustomExitTakesMultipleValues500(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123,500",
                                custom_exit_behaviour=Task.CONTINUE)
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_custom_continue", [],
                          {}, None, 1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Completed step: 1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=123)
    def testCustomExitFails(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123",
                                custom_exit_behaviour=Task.FAIL)
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 1, 1, 1,
                          "test_custom_continue", [], {}, None, 1, {})

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=123)
    def testCustomExitFailsIfGivenNonNumbericalExitStatuses(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123,ARGHEL",
                                custom_exit_behaviour=Task.FAIL)
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 1, 1, 1,
                          "test_custom_continue", [], {}, None, 1, {})

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=123)
    def testCustomExitTerminates(self, m):
        '''
            If we set an alternate exit status and that the job should continue
            then we should see the job end at the 2nd task
        '''
        t2 = TaskFactory.create(backend=self.b, name="test_custom_continue",
                                executable="grep 'previous' /tmp/",
                                in_glob="in", out_glob="out",
                                custom_exit_status="123",
                                custom_exit_behaviour=Task.TERMINATE)
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_custom_continue", [],
                          {}, None, 1, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Completed job at step #1")
