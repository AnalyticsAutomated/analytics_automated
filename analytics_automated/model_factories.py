import random
import string
import factory
import uuid
import os
from unipath import Path

from django.test import TestCase
from django.conf import settings
from django.core.files import File

from .models import Backend, Task, Job, Step, Submission
from .models import Parameter, Result, Validator

TEST_DATA = settings.BASE_DIR.child("static").child("files").child("file1.txt")
RESULT_DATA = settings.BASE_DIR.child("static").child("files"). \
                                                child("result1.txt")
step_value = random.randint(1, 20)


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class BackendFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'test_{}'.format(n))
    server_type = Backend.LOCALHOST
    # ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    # port = random.randint(1, 65325)
    root_path = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Backend
        django_get_or_create = ('name',)


class TaskFactory(factory.DjangoModelFactory):
    backend = factory.SubFactory(BackendFactory)
    name = factory.Sequence(lambda n: 'task_{}'.format(n))
    in_glob = factory.LazyAttribute(lambda t: random_string())
    out_glob = factory.LazyAttribute(lambda t: random_string())
    executable = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Task
        django_get_or_create = ('name',)


class JobFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'job_{}'.format(n))
    runnable = True

    class Meta:
        model = Job
        django_get_or_create = ('name',)


class StepFactory(factory.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    task = factory.SubFactory(TaskFactory)
    ordering = random.randint(0, 20)

    class Meta:
        model = Step


class SubmissionFactory(factory.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    submission_name = factory.Sequence(lambda n: 'submission_{}'.format(n))
    UUID = factory.LazyAttribute(lambda t: str(uuid.uuid1()))
    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    input_data = factory.LazyAttribute(lambda t: File(open(TEST_DATA)))

    class Meta:
        model = Submission
        django_get_or_create = ('submission_name',)


class ParameterFactory(factory.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    flag = factory.LazyAttribute(lambda t: random_string())
    default = factory.LazyAttribute(lambda t: random_string())
    bool_valued = True
    rest_alias = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Parameter


class ValidatorFactory(factory.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    validation_type = random.randint(0, 2)
    re_string = ".+"

    class Meta:
        model = Validator


class ResultFactory(factory.DjangoModelFactory):
    submission = factory.SubFactory(SubmissionFactory)
    task = factory.SubFactory(TaskFactory)
    step = step_value
    previous_step = step_value-1
    result_data = factory.LazyAttribute(lambda t: File(open(RESULT_DATA)))
    name = factory.LazyAttribute(lambda t: random_string())
    message = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Result
