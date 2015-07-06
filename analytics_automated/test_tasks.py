import uuid

from unittest.mock import patch

from commandRunner.localRunner import *
from django.test import TestCase

from .tasks import *
from .models import Submission
from .model_factories import *


class TaskTestCase(TestCase):

    uuid1 = ""
    b = None
    t = None
    j = None
    s = None
    sub = None

    def testTrivialAdd(self):
        """
            Here we test that our task_runner function does it's thing
        """
        result = add.delay(8, 8)

        self.assertEquals(result.get(), 16)
        self.assertTrue(result.successful())

    def setUp(self):
        self.uuid1 = str(uuid.uuid1())
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="test_task",
                                    executable="ls")
        self.j = JobFactory.create()
        self.s = StepFactory(job=self.j, task=self.t, ordering=0)
        self.sub = SubmissionFactory.create(UUID=self.uuid1, job=self.j)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTestTaskRunnerSuccess(self, m):
        result = task_runner.delay(self.uuid1, 0, 0, 1, "test_task")
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual((self.sub.message == "Completed step :0"), True)

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=1)
    def testTestTaskRunnerExecuteNoneZeroExit(self, m):
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 0, 1,
                          "test_task")
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual((self.sub.message == "Failed step :0"), True)
