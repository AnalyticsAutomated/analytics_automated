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
        step_value = random.randint(1, 20)
        self.uuid1 = str(uuid.uuid1())
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="test_task",
                                    executable="grep 'previous' $INPUT > $OUTPUT",
                                    in_glob="txt", out_glob="out")
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
    def testTaskRunnerSuccess(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, "test_task", [], {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual((self.sub.message == "Completed at step #1"), True)

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=1)
    def testTaskRunnerExecuteNoneZeroExit(self, m):
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 1, 1,
                          "test_task", [], {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual((self.sub.message == "Failed step :0"), True)

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerSignalsRunningWhenNotAtLastStep(self, m):
        task_runner.delay(self.uuid1, 0, 1, 2, "test_task", [], {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual((self.sub.message == "Running"), True)

    def testTaskRunnerDoesGetResultFromPreviousRun(self):
        '''
            this tests that it got the previous results correctly. It can only
            write the correct new result entry if it did so
        '''
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        task_runner.delay(self.uuid1, 0, 2, 2, "test_task", [], {})
        result = Result.objects.get(submission=self.sub, step=2)
        data = ''
        result.result_data.open(mode='r')
        for line in result.result_data:
            data += line.decode(encoding='UTF-8')
        result.result_data.close()
        self.assertEqual((data == "Here is some previous results!\n"), True)
