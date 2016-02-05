import json
import io
import uuid
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
from rest_framework.request import Request

from .api import SubmissionDetails
from .models import *
from .model_factories import *
from .tasks import *


def tearDown(self):
    print("hello")
    Backend.objects.all().delete()
    Job.objects.all().delete()
    Task.objects.all().delete()
    Step.objects.all().delete()
    Submission.objects.all().delete()
    Parameter.objects.all().delete()
    Result.objects.all().delete()
