import glob
import os

from analytics_automated.models import Backend, Task, Job, Parameter
from analytics_automated.models import Step, Submission, Validator, Result
from .model_factories import *

'''
    useful routines the test classes make repeated use of
'''


def clearDatabase():
    Backend.objects.all().delete()
    Job.objects.all().delete()
    Task.objects.all().delete()
    Step.objects.all().delete()
    Submission.objects.all().delete()
    Parameter.objects.all().delete()
    Result.objects.all().delete()
    SubmissionFactory.reset_sequence()
    JobFactory.reset_sequence()
    for file_1 in glob.glob(settings.BASE_DIR.child("submissions") +
                            "/file1*"):
        os.remove(file_1)
    for example in glob.glob(settings.BASE_DIR.child("submissions") +
                             "/example*"):
        os.remove(example)
    for example in glob.glob(settings.BASE_DIR.child("submissions") +
                             "/result1*"):
        os.remove(example)
    for example in glob.glob(settings.BASE_DIR.child("submissions") +
                             "/huh*"):
        os.remove(example)