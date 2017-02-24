import uuid

from django.test import TestCase
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from .models import Backend, Task, Job, Step, Submission, Validator
from .model_factories import *


class BackendMethodTests(TestCase):
    # tests are quite thin for most of these as there isn't much
    # clever happening and we try not to test django functionality.
    def test_backend_accepts_valid_data(self):
        """
            check that we can load some valid data
        """
        b = BackendFactory.create()
        self.assertEqual((Backend.objects.count() == 1), True)

    def test_rejects_invalid_ip(self):
        """
            check wierd IPs can not be accepted
        """
        error_ocurred = False
        try:
            with transaction.atomic():
                b = BackendFactory.create(ip='128.0.0.4.5')
        except Exception as e:
            self.assertEqual((Backend.objects.count() == 0), True)
            error_ocurred = True
        self.assertTrue(error_ocurred)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class TaskMethodTest(TestCase):

    def test_task_accepts_valid_data(self):
        """
            check we can load valid task data
        """
        b = BackendFactory.create()
        t = TaskFactory.create(backend=b)
        self.assertEqual(Task.objects.count(), 1)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class JobMethodTest(TestCase):

    def test_job_accepts_valid_data(self):
        """
            check we can load valid job data
        """
        j = JobFactory.create()
        self.assertEqual(Job.objects.count(), 1)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class StepMethodTest(TestCase):

    def test_step_accepts_valid_data(self):
        """
           check we can add steps
        """
        b = BackendFactory.create()
        t = TaskFactory.create(backend=b)
        j = JobFactory.create()
        s = StepFactory(job=j, task=t, ordering=0)
        s = StepFactory(job=j, task=t, ordering=1)
        self.assertEqual(Step.objects.count(), 2)

    # DB : removed to support concurrent tasks
    # def test_steps_can_not_have_same_ordering(self):
    #     """
    #         Checks the same step order value is not allowed for a given job
    #     """
    #     b = BackendFactory.create()
    #     t = TaskFactory.create(backend=b)
    #     j = JobFactory.create()
    #     s = StepFactory(job=j, task=t, ordering=0)
    #     error_occurred = False
    #     try:
    #         with transaction.atomic():
    #             s = StepFactory(job=j, task=t, ordering=0)
    #     except Exception as e:
    #         error_ocurred = True
    #     self.assertTrue(error_ocurred)

    def test_ensure_all_steps_are_removed_on_job_deletion(self):
        b = BackendFactory.create()
        t = TaskFactory.create(backend=b)
        j = JobFactory.create()
        s = StepFactory(job=j, task=t, ordering=0)
        s = StepFactory(job=j, task=t, ordering=1)
        Job.objects.all().delete()
        self.assertEqual(Step.objects.count(), 0)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class SubmissionTest(TestCase):

    def test_submission_insertion(self):
        """
            simple data loading test
        """
        s = SubmissionFactory.create()
        self.assertEqual(Submission.objects.count(), 1)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class ValidatorTest(TestCase):

    v = None

    def tearDown(self):
        Job.objects.all().delete()
        Validator.objects.all().delete

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()


class ParameterTest(TestCase):

    def test_parameter_submission(self):
        p = ParameterFactory.create()
        self.assertEqual(Parameter.objects.count(), 1)

    def test_rest_alias_takes_task_name(self):
        b = BackendFactory.create()
        t = TaskFactory.create(backend=b, name="test")
        p = ParameterFactory.create(task=t, rest_alias="alias")
        self.assertEqual(p.rest_alias, t.name+"_alias")

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()
