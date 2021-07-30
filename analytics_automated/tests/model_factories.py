import random
import string
import factory
import uuid
import os
from unipath import Path

from django.test import TestCase
from django.conf import settings
from django.core.files import File

from analytics_automated.models import Backend, Task, Job, Step, Batch
from analytics_automated.models import Submission, ValidatorTypes
from analytics_automated.models import Parameter, Result
from analytics_automated.models import Validator, Environment, QueueType
from analytics_automated.models import Configuration


TEST_DATA = settings.BASE_DIR.child("submissions").child("files"). \
                                                   child("file1.txt")
RESULT_DATA = settings.BASE_DIR.child("submissions").child("files"). \
                                                     child("result1.txt")
step_value = random.randint(1, 20)


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class QueueTypeFactory(factory.django.DjangoModelFactory):
    name = "localhost"
    execution_behaviour = QueueType.LOCALHOST

    class Meta:
        model = QueueType
        django_get_or_create = ('name',)


class BackendFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'test_{}'.format(n))
    queue_type = factory.SubFactory(QueueTypeFactory)
    # ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    # port = random.randint(1, 65325)
    root_path = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Backend
        django_get_or_create = ('name',)


class TaskFactory(factory.django.DjangoModelFactory):
    backend = factory.SubFactory(BackendFactory)
    name = factory.Sequence(lambda n: 'task_{}'.format(n))
    in_glob = factory.LazyAttribute(lambda t: random_string())
    out_glob = factory.LazyAttribute(lambda t: random_string())
    executable = factory.LazyAttribute(lambda t: random_string())
    incomplete_outputs_behaviour = Task.CONTINUE
    custom_exit_status = None
    custom_exit_behaviour = None

    class Meta:
        model = Task
        django_get_or_create = ('name',)


class ConfigurationFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    type = random.randint(0, 2)
    name = factory.LazyAttribute(lambda t: random_string())
    parameters = factory.LazyAttribute(lambda t: random_string())
    version = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Configuration


class JobFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'job_{}'.format(n))
    runnable = True

    class Meta:
        model = Job
        django_get_or_create = ('name',)


class StepFactory(factory.django.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    task = factory.SubFactory(TaskFactory)
    ordering = random.randint(0, 20)

    class Meta:
        model = Step


class BatchFactory(factory.django.DjangoModelFactory):
    UUID = factory.LazyAttribute(lambda t: str(uuid.uuid1()))
    status = random.randint(0, 4)

    class Meta:
        model = Batch


class SubmissionFactory(factory.django.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    submission_name = factory.Sequence(lambda n: 'submission_{}'.format(n))
    UUID = factory.LazyAttribute(lambda t: str(uuid.uuid1()))
    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    input_data = factory.django.FileField(from_path=TEST_DATA)
    # status = random.randint(0, 4)
    batch = factory.SubFactory(BatchFactory)
    hostname = "localhost"

    class Meta:
        model = Submission
        django_get_or_create = ('submission_name',)


class ParameterFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    flag = factory.LazyAttribute(lambda t: random_string())
    default = factory.LazyAttribute(lambda t: random_string())
    bool_valued = True
    rest_alias = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Parameter


class EnvironmentFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    env = factory.LazyAttribute(lambda t: random_string())
    value = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Environment


class ValidatorTypesFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = ValidatorTypes


class ValidatorFactory(factory.django.DjangoModelFactory):
    job = factory.SubFactory(JobFactory)
    validation_type = factory.SubFactory(ValidatorTypesFactory)

    class Meta:
        model = Validator


class ResultFactory(factory.django.DjangoModelFactory):
    submission = factory.SubFactory(SubmissionFactory)
    task = factory.SubFactory(TaskFactory)
    step = step_value
    previous_step = step_value-1
    result_data = factory.django.FileField(from_path=RESULT_DATA)
    name = factory.LazyAttribute(lambda t: random_string())
    message = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Result
