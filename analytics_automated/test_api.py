import json
import io
from unipath import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from .api import SubmissionDetails
from .models import Job, Submission
from .model_factories import *
from .tasks import *


class JobListTests(APITestCase):

    def test_return_of_available_job_types(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")
        response = self.client.get(reverse('job',)+".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"count":2,"next":null,"previous":null,' \
                    '"results":[{"pk":1,"name":"job1"},{"pk":2,"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

        def tearDown(self):
            Backend.objects.all().delete()
            Job.objects.all().delete()
            Task.objects.all().delete()
            Step.objects.all().delete()
            Submission.objects.all().delete()
            Parameter.objects.all().delete()
            Result.objects.all().delete()


class SubmissionDetailTests(APITestCase):

    file = ''
    data = {}
    factory = APIRequestFactory()

    def setUp(self):
        self.file = SimpleUploadedFile('file1.txt',
                                       bytes('these are the file contents!',
                                             'utf-8'))
        self.data = {'input_data': self.file,
                     'job': 'job1',
                     'submission_name': 'test',
                     'email': 'a@b.com'}
        j1 = JobFactory.create(name="job1")
        b = BackendFactory.create(root_path="/tmp/")
        t = TaskFactory.create(backend=b, name="task1", executable="ls")
        s = StepFactory(job=j1, task=t, ordering=0)

    def tearDown(self):
        Backend.objects.all().delete()
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Submission.objects.all().delete()
        Parameter.objects.all().delete()
        Result.objects.all().delete()

    def test_submission_detail_is_returned(self,):
        s1 = SubmissionFactory.create()
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.UUID, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{"submission_name":"submission_1","UUID":"%s"' \
                    ',"state":"Submitted"}' % s1.UUID
        self.assertEqual(response.content.decode("utf-8"), test_data)

    @patch('builtins.eval', return_value=True)
    def test_valid_submission_post_creates_entry(self, m):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rejection_with_bad_email(self):
        self.data['email'] = 'b'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_with_bad_job_id(self):
        self.data['job'] = 'job34'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_rejection_with_blank_submission_name(self):
        self.data['submission_name'] = ""
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_submission_name(self):
        del(self.data['submission_name'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_email(self):
        del(self.data['email'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_job(self):
        del(self.data['job'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejection_without_input_data(self):
        del(self.data['input_data'])
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
