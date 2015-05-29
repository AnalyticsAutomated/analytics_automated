import uuid

from django.test import TestCase
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile


from .models import Backend, Task, Job, Step, Submission


# some helper methods with defined data for calling in the tests
def save_good_backend():
    b = Backend(name='test', server_type=Backend.GRIDENGINE,
                ip="128.0.0.4", port=80, root_path="/tmp/")
    b.save()
    return(b)


def save_bad_ip_backend():
    b = Backend(name='test', server_type=Backend.GRIDENGINE,
                ip='128.0.0.4.5', port=80, root_path="/tmp/")
    b.save()
    return(b)


def save_good_task(b):
    t = Task(backend=b, name='task1', in_glob="in", out_glob="out",
             executable="/usr/bin/ls")
    t.save()
    return(t)


def save_good_job():
    j = Job(name='job', runnable=True)
    j.save()
    return(j)


def save_good_step(j, t, o):
    s = Step(job=j, task=t, ordering=o)
    s.save()
    return(s)


def save_good_submission(j, name, uuid, email, ip, data):
    s = Submission(job=j, submission_name=name, UUID=uuid,
                   ip=ip, input_data=data)
    s.save()
    return(s)


class BackendMethodTests(TestCase):
    # tests are quite thin for most of these as there isn't much
    # clever happening and we try not to test django functionality.
    def test_backend_accepts_valid_data(self):
        """
            check that we can load some valid data
        """
        b = save_good_backend()
        self.assertEqual((b.name == 'test'), True)
        self.assertEqual((Backend.objects.count() == 1), True)

    def test_rejects_invalid_ip(self):
        """
            check wierd IPs can not be accepted
        """
        error_ocurred = False
        try:
            with transaction.atomic():
                b = save_bad_ip_backend()
        except Exception as e:
            self.assertEqual((Backend.objects.count() == 0), True)
            error_ocurred = True
        self.assertTrue(error_ocurred)


class TaskMethodTest(TestCase):

    def test_task_accepts_valid_data(self):
        """
            check we can load valid task data
        """
        b = save_good_backend()
        t = save_good_task(b)
        self.assertEqual((t.name == 'task1'), True)
        self.assertEqual((Task.objects.count() == 1), True)


class JobMethodTest(TestCase):

    def test_job_accepts_valid_data(self):
        """
            check we can load valid job data
        """
        j = save_good_job()
        self.assertEqual((j.name == 'job'), True)
        self.assertEqual((Job.objects.count() == 1), True)


class StepMethodTest(TestCase):

    def test_step_accepts_valid_data(self):
        """
           check we can add steps
        """
        b = save_good_backend()
        t = save_good_task(b)
        j = save_good_job()
        s = save_good_step(j, t, 0)
        s = save_good_step(j, t, 1)
        self.assertEqual((Step.objects.count() == 2), True)

    def test_steps_can_not_have_same_orderinge(self):
        """
            Checks the same step order value is not allowed for a given job
        """
        b = save_good_backend()
        t = save_good_task(b)
        j = save_good_job()
        s = save_good_step(j, t, 0)
        error_occurred = False
        try:
            s = save_good_step(j, t, 0)
        except Exception as e:
            error_ocurred = True
        self.assertTrue(error_ocurred)

    def test_ensure_all_steps_are_removed_on_job_deletion(self):
        b = save_good_backend()
        t = save_good_task(b)
        j = save_good_job()
        s = save_good_step(j, t, 0)
        s = save_good_step(j, t, 1)
        Job.objects.all().delete()
        self.assertEqual((Step.objects.count() == 0), True)


class SubmissionTest(TestCase):

    def test_submission_insertion(self):
        """
            simple data loading test
        """
        j = save_good_job()
        id1 = str(uuid.uuid1())
        file1 = SimpleUploadedFile('file1.txt',
                                   bytes('these are the file contents!', 'utf-8'))
        s = save_good_submission(j, "name", id1, "a@b.com", "127.0.0.1", file1)
        self.assertEqual((Submission.objects.count() == 1), True)
