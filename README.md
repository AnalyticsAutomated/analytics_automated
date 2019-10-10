# analytics_automated

### Continue:

Analytics Automated (A_A) is a 'lightweight' framework for automating long running
distributed computation principally focused on executing Data Science tasks.

Today it is trivially easy for Scientists, Researchers, Data Scientists and
Analysts to build statistical and predictive models. More often than not these
don't get turned in to useful and usable services; frequently becoming reports
on work which does not get actioned. In short, organisations often have trouble
operationalising the models and insights which emerge from complex statistical
research and data science.

Analytics automated is targeted at streamlining the process for turning your
predictive software into usable and maintainable services.

With A_A Researchers and data scientists can build models in the modelling tool
of their choice and then, with trivial configuration, Analytics Automated will
turn these models in to an easy to use API for integration in to websites and
other tools.

The other principal benefit of this system is to reduce technology lock-in.
Statistical modelling and Data Science expertise is now spread across a wide
range of technologies (Hadoop, SAS, R and more) and such technological
proliferation shows no sign of slowing down. Picking a single modeling
technology greatly reduces the pool of possible employees for your organisation
and backing the "wrong horse" means if you have to change it can be very costly
in terms of time, staffing and money.

A_A is agnostic to the modeling software and technologies you choose to build
your group around.

### Philosophy

A_A exists because one way or another I have implemented some version of this
system in nearly every job I have held. In a large part this exists so I never
have to implement this kind of system, from scratch, again. Hopefully some others
folk can get some use out of it.

Broadly A_A allows you to configure simple chains of python-Celery tasks. You
certainly don't have to use the system for Data Science-y things but execution of
number crunching tasks is our target. You find R, SciPy and NumPy support is
rolled in to the system.

A_A tries to be very unopinionated about the kinds of things that computational
tasks consume and produce. The upside is that it is versatile, the
downside is that you still need to be something of a programmer to get the most
out of this tool.

### How it works

Users send data as a REST POST request call to a pre-configured analysis or
prediction task and after some asynchronous processing they can come back and
GET their results. It's as simple as that and you are free to build this in
to any system you have or build the UI of your choice.

### Roadmap

1. SVG graphs for job progress.

# Requirements

You will need

* python3
* postgres
* Redis
* django
* celery

NEXT UP TODO/REMINDERS
======================

1. On Submission delete propagate message to workers to kill task
2. Non-linear jobs (i.e tasks with multiple parents, full DAG support), see CWL support
3. Add CWL support to configure and dump tasks/jobs. Consider importing
   Toil library to handle parsing the yaml and pushing the results to the db
4. Further backends, Octave, matlab, SAS

Production things:

5. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

    enable app.Task.track_started
    Autoscaling
    don't run in DEBUG mode

6. Solution for file storage in staging/production???
7. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
8. Investigate cached_property

Missing
=======
1. Robust to task failure. Some types of exception should probably be tried again and some failures should propagate to the user, likely need to some way to let the users configure this in a task
http://agiliq.com/blog/2015/08/retrying-celery-failed-tasks/
http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying-a-task-if-something-fails
2. Let jobs run jobs as nested structures; this will be part of adding CWL support

THINGS FOR ANSIBLE update
=========================

    pip install -U "celery[redis]"
    sudo yum install redis
    redis-server (now runs on port 6379, not much point in adding authentication)
