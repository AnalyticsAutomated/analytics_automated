import glob

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase

from rest_framework.test import APIRequestFactory

from .model_factories import *
from analytics_automated.forms import *
from .helper_functions import clearDatabase

class TaskForms(TestCase):

    file = ''
    data = {}
    factory = APIRequestFactory()
    j1 = None
    t = None
    b = None

    def setUp(self):
        self.file = SimpleUploadedFile('file1.txt',
                                       bytes('these are the file contents!',
                                             'utf-8'))
        self.data = {'input_data': self.file,
                     'job': 'job1',
                     'submission_name': 'test',
                     'email': 'a@b.com'}
        self.j1 = JobFactory.create(name="job1")
        self.b = BackendFactory.create(root_path="/tmp/")
        self.t = TaskFactory.create(backend=self.b, name="task1",
                                    executable="ls")
        s = StepFactory(job=self.j1, task=self.t, ordering=0)

    def tearDown(self):
        clearDatabase()

    def test__validate_input_accepts_png(self):
        vt = ValidatorTypesFactory.create(name='png')
        v = ValidatorFactory.create(job=self.j1, validation_type=vt)
        validators = self.j1.validators.all()
        sf = SubmissionForm()
        f = open("submissions/files/test.png", "rb").read()
        pngFile = SimpleUploadedFile('test.png', f)
        s = SubmissionFactory.create(input_data=File(pngFile))
        self.assertTrue(sf._SubmissionForm__validate_input(validators,
                        s.input_data))

    def test__validate_input_rejects_gif(self):
        vt = ValidatorTypesFactory.create(name='png')
        v = ValidatorFactory.create(job=self.j1, validation_type=vt)
        validators = self.j1.validators.all()
        sf = SubmissionForm()
        f = open("submissions/files/test.gif", "rb").read()
        pngFile = SimpleUploadedFile('test.gif', f)
        s = SubmissionFactory.create(input_data=File(pngFile))
        self.assertFalse(sf._SubmissionForm__validate_input(validators,
                         s.input_data))
