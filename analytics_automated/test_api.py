import json
import io
from unipath import Path

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


class JobListTests(APITestCase):

    def test_return_of_available_job_types(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")
        response = self.client.get(reverse('job',)+".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"count":2,"next":null,"previous":null,"results":[{"pk":1,"name":"job1"},{"pk":2,"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)


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

    def test_submission_detail_is_returned(self):
        s1 = SubmissionFactory.create()
        response = self.client.get(reverse('submissionDetail',
                                           args=[s1.pk, ]) + ".json")
        self.assertEqual(response.status_code, 200)
        test_data = '{"submission_name":"submission_0","UUID":"'+s1.UUID+'"}'
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_valid_submission_post_creates_entry(self):
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rejectiong_with_bad_email(self):
        self.data['email'] = 'b'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejectiong_with_bad_email(self):
        self.data['job'] = 'job34'
        request = self.factory.post(reverse('submission'), self.data,
                                    format='multipart')
        view = SubmissionDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
