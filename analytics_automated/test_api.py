import json
from unipath import Path

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.conf import settings

from .models import Job, Submission
from .model_factories import *
from django.core.files.uploadedfile import SimpleUploadedFile

class SubmissionDetailTests(TestCase):

    def test_submissiondetail_returns_an_available_submission(self):
        s = SubmissionFactory.create()
        response = self.client.get(reverse('submission_detail',
                                           args=(s.pk,)))
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['submission_name'], s.submission_name)

    def test_submissiondetail_404_on_non_existing(self):
        s = SubmissionFactory.create()
        response = self.client.get(reverse('submission_detail',
                                           args=(100000,)))
        self.assertEqual(response.status_code, 404)


class SubmissionCreateTests(TestCase):

    def test_submissioncreate_will_accept_data(self):

        f = SimpleUploadedFile("file.txt", bytes("file_content", 'utf-8'))
        #     "list": {
        #         "name": "test name",
        #         "description": "test description"
        #     }
        # })
        # form = {
        #     "file": f,
        #     "json": my_json,
        # }
        response = self.client.post(reverse('submission_data'), {'input_data': f, 'submission_name': 'test'}, content_type = 'multipart/form-data')
        self.assertEqual(response.status_code, 200)
        # response = self.client.post(reverse('submission_data'),
        #                             payload, content_type = 'application/x-www-form-urlencoded')
        #
        print(response.status_code)


                    # { 'input_data': fp, 'submission_name': 'test' }, kwargs={ 'job_name': 'job1',
                    #
                    #        'email': 'a@b.com'
                    #      }  )
