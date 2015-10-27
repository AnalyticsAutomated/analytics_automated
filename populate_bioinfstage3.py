# Short script populates the database with some test/example data
#
#
import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'analytics_automated_project.settings.dev')

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile

from analytics_automated.models import Backend, Job, Task, Step
from analytics_automated.models import Parameter, Submission, Result
from analytics_automated.models import Validator, BackendUser


def populate():

    this_backend = add_backend(name="local1",
                               server_type=Backend.GRIDENGINE,
                               ip="127.0.0.1",
                               port=80,
                               root_path="/webdata/")
    this_backenduser = add_BackendUser(backend=this_backend,
                                       userid="default",
                                       password="p4ssw0rd",
                                       priority=2)
    this_task = add_task(backend=this_backend,
                         name="ls_ge_task",
                         in_glob=".in",
                         out_glob=".out",
                         executable="ls $FLAGS > $OUTPUT")

    this_param = add_parameter(task=this_task,
                               flag="-lah",
                               default=true,
                               bool_valued=t,
                               rest_alias="list_all")

    this_job = add_job(name="ge_test_job",
                       runnable=True)

    add_step(this_job, this_task, 0)


def add_backend(name, server_type, ip, port, root_path):
    b = Backend.objects.create(name=name)
    b.server_type = server_type
    b.ip = ip
    b.port = port
    b.root_path = root_path
    b.save()
    return b


def add_task(backend, name, in_glob, out_glob, executable):
    t = Task.objects.create(backend=backend)
    t.name = name
    t.in_glob = in_glob
    t.out_glob = out_glob
    t.executable = executable
    t.save()
    return t


def add_parameter(task, flag, default, bool_valued, rest_alias):
    p = Parameter.objects.create(task=task)
    p.flag = flag
    p.default = default
    p.bool_valued = bool_valued
    p.rest_alias = rest_alias
    p.save()
    return p


def add_job(name, runnable):
    j = Job.objects.create(name=name)
    j.runnable = True
    j.save()
    return j


def add_step(job, task, ordering):
    s = Step.objects.create(job=job, task=task, ordering=ordering)
    s.save()
    return s


def add_submisson(job, name, UUID, email, ip, input_data):
    s = Submission.objects.create(job=job)
    s.submission_name = name
    s.UUID = UUID
    s.email = email
    s.ip = ip
    s.input_data = input_data
    s.save()
    return(s)


def add_validator(job, val_type, re_string):
    v = Validator.objects.create(job=job)
    v.validation_type = val_type
    v.re_string = re_string
    v.save()
    return(v)


def add_BackendUser(backend, userid, password, priority):
    bu = BackendUser.objects.create(backend=backend)
    bu.login_name = userid
    bu.password = password
    bu.priority = priority
    bu.save()

# Start execution here!
if __name__ == '__main__':
    print("Starting A_A population script...")
    populate()
