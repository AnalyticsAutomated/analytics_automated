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

TEST_DATA = settings.BASE_DIR.child("static").child("files").child("file1.txt")


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class BackendFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'test_{}'.format(n))
    server_type = Backend.LOCALHOST
    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    port = random.randint(1, 65325)
    root_path = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Backend
        django_get_or_create = ('name',)


class TaskFactory(factory.DjangoModelFactory):
    backend = BackendFactory.create()
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
    job = JobFactory.create()
    task = TaskFactory.create()
    ordering = random.randint(0, 20)

    class Meta:
        model = Step


class SubmissionFactory(factory.DjangoModelFactory):
    job = JobFactory.create()
    submission_name = factory.Sequence(lambda n: 'submission_{}'.format(n))
    UUID = str(uuid.uuid1())
    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    input_data = factory.LazyAttribute(lambda t: File(open(TEST_DATA)))

    class Meta:
        model = Submission
        django_get_or_create = ('submission_name',)
