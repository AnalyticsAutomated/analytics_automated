import json
from unipath import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Job, Submission
from .model_factories import *


class JobListTests(APITestCase):

    def test_return_of_available_job_types(self):
        j1 = JobFactory.create(name="job1")
        j2 = JobFactory.create(name="job2")
        data = {'name': 'DabApps'}
        response = self.client.get(reverse('job',)+".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        test_data = '{"count":2,"next":null,"previous":null,"results":[{"pk":1,"name":"job1"},{"pk":2,"name":"job2"}]}'
        self.assertEqual(response.content.decode("utf-8"), test_data)


class SubmissionDetailTests(APITestCase):

    def test_submission_detail_is_returned(self):
        pass
