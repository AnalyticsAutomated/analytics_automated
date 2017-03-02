.. _advanced_uses:

Advanced Uses
=============

A_A is implemented in python and Django to make it easy for others to extend.
This document covers the programmatic details of A_A to help this

System details
^^^^^^^^^^^^^^

The following is an overview of the execution path for user data submissions.
There are principaaly 2 important functions api.post() and tasks.taskrunner().

Users make POST requests with files of data to the django webserver and these
arrive at the `post()`` method in the `apy.py`. The post() method is
responsible for validating data and dispatching jobs to the workers.

post() runs through the following sequence of events.

* The incoming POST data is checked to ensure that all the required elements are present
* We doublecheck how many jobs a user has submitted and assigns there submission to a queue
* Data is then run through the standard Django form validation process
* And... during form validation and custom data validation the job requires is executed
* If validation passes the function identifies the job that was requested and constructs a celery chain including all the job's tasks
* finally the chain is submitted to the celery queue.

Once a job is pushed to the queue it will be picked up by any workers listening to
that queue. `tasks.py` defines celery functions which execute the job. The
principal one is `task_runner()

task_runner() receives all the information required to query the database for
all the details required to run a task. Having compiled this data it then uses
the python module commandRunner to execute the task. It will catch any problems,
handle different exit statuses and push the results back to the database. If
enabled and configured correctly it will email the user when the job completes.

New validators
^^^^^^^^^^^^^^

By default we provide a number of pre-written validation functions that can sanity
check incoming data submissions. A validator is a function that reads a file
and returns True of False if the data is acceptable.

A validator is a regular python function that returns True or False. Once
written the system will pick up new functions and make them available in the '+ Add Job'
dialogue. In Django development mode this process is automatic. For a production system
you will need to restart the Django server. Functions beginning with '_' will be regarded
as private and will not be added to the validators

Programmatic Admin
^^^^^^^^^^^^^^^^^^

As A_A is a regualr Django application it is possible to configure tasks, jobs, backends, queues programmatically

We provide examples of this in the example_scripts/ directory, populate_analytics_automated.py gives and example of performing this.
models.py explains the database schema and the the fields that users can set.

Yaml upload and download
^^^^^^^^^^^^^^^^^^^^^^^^

If programmatic or web access is not suitable, it is also possible to dump the
job configurations to yaml or upload new configuration if the

Adding new celery queues
^^^^^^^^^^^^^^^^^^^^^^^^
