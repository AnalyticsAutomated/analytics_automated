import glob
import os

from analytics_automated.models import Backend, Task, Job, Parameter, Batch
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
    Batch.objects.all().delete()

    BackendFactory.reset_sequence(0)
    JobFactory.reset_sequence(0)
    TaskFactory.reset_sequence(0)
    StepFactory.reset_sequence(0)
    SubmissionFactory.reset_sequence(0)
    ParameterFactory.reset_sequence(0)
    ResultFactory.reset_sequence(0)
    BatchFactory.reset_sequence(0)

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
