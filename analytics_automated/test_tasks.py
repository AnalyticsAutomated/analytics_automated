from django.test import TestCase
from .tasks import *


class TaskTestCase(TestCase):

    def testTrivialAdd(self):
        """
            Here we test that our task_runner function does it's thing
        """
        result = add.delay(8, 8)

        self.assertEquals(result.get(), 16)
        self.assertTrue(result.successful())

    def testTestRunnerLocalRunnerSuccess(self):
        # make a sane submission, task and backend object
        # mock the localRunner
        # result = task_runner.delay(uuid, step_id, current_step,
        #                            total_steps, task_name)
        pass
