import uuid
import glob
import os

from unittest.mock import patch

from commandRunner.localRunner import *

from django.test import TestCase
from django.test import override_settings

from .tasks import *
from analytics_automated import tasks
from .models import Submission, Message
from .model_factories import *


class TaskTestCase(TestCase):
    uuid1 = ""
    b = None
    t = None
    j = None
    s = None
    sub = None
    messages = None

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
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()
        Message.objects.all().delete()
        for file_1 in glob.glob(settings.BASE_DIR.child("submissions")+"/file1*"):
            os.remove(file_1)
        for example in glob.glob(settings.BASE_DIR.child("submissions")+"/example*"):
            os.remove(example)
        for example in glob.glob(settings.BASE_DIR.child("submissions")+"/result1*"):
            os.remove(example)

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerSuccess(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 1, "test_task", [], {}, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        #print(self.sub)
        self.assertEqual(self.sub.last_message, "Completed job at step #1")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerAllMessagesSent(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 1, "test_task", [], {}, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.messages = Message.objects.all().filter(submission=self.sub)
        # for m in self.messages:
        #     print(str(m))
        self.assertGreater(len(self.messages), 1)

    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=1)
    def testTaskRunnerExecuteNoneZeroExit(self, m):
        self.assertRaises(OSError, task_runner, self.uuid1, 0, 1, 1, 1,
                          "test_task", [], {}, {})
        self.sub = Submission.objects.get(UUID=self.uuid1)
        self.assertEqual(self.sub.last_message, "Failed step, non 0 exit at step:0")

    @override_settings(
        task_eager_propagates=True,
        task_always_eager=True,
        broker_url='memory://',
        backend='memory',
    )
    @patch('analytics_automated.tasks.localRunner.run_cmd', return_value=0)
    def testTaskRunnerSignalsRunningWhenNotAtLastStep(self, m):
        task_runner.delay(self.uuid1, 0, 1, 1, 2, "test_task", [], {}, {})
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
        task_runner.delay(self.uuid1, 0, 2, 2, 2, "test_task", [], {}, {})
        result = Result.objects.get(submission=self.sub, step=2)
        self.assertEqual(result.message, "Result")

    def test_get_data_correctly_gets_input_data(self):
        data, previous_step = tasks.get_data(self.sub, self.sub.UUID, 1,
                                             [".txt", ])
        self.assertEqual(data, {self.sub.UUID+".txt": "these are the file contents!\n"})

    def test_get_data_correctly_gets_previous_data(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 2,
                                             [".txt"])
        self.assertEqual(data, {res.result_data.name: "Here is some previous results!\n"})

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
                         {res2.result_data.name: "Here is some previous results!\n",
                          res.result_data.name: "Here is some previous results!\n"
                          })

    def test_only_gets_previous_data_when_there_is_an_inglobs_match(self):
        res = ResultFactory.create(submission=self.sub,
                                   task=self.t,
                                   step=1,
                                   previous_step=None,)
        data, previous_step = tasks.get_data(self.sub, res.submission.UUID, 2,
                                             [".csv"])
        self.assertEqual(data, {})
