.. _advanced_uses:

Advanced Uses
=============

A_A is implemented in python and Django to make it easy for others to extend.
This document covers some programmatic details of A_A to help this

System details
^^^^^^^^^^^^^^

The following is an overview of the execution path for user data submissions.
There are principally 2 important functions api.post() and tasks.taskrunner().

Users make POST requests with files of data to the django webserver and these
arrive at the `post()` method in the `api.py`. The post() method is
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
principal one is `task_runner()`

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

The simplest possible validator would do nothing with the file

::

  def simple_validator(file_data):
      return(True)

A more realistic validator needs to interogate the contents of the file.
the data passsed in is always a byte stream from a file. So typically the first
thing you wish to do would be to decode the byte stream. In the example below
the validator would return False is every line does not start with a '#'

::

  def better_validator(file_data):
      data_string = file_data.decode("utf-8")
      for line in  string_data.splitlines():
        if not line.startswith('#')
          return False
      return True

When writing validators you can add tests to the test_validators.py file and
use the typical Django test command to test them. If you remove a validator,
don't forget to remove its associated tests

Programmatic Admin
^^^^^^^^^^^^^^^^^^

As A_A is a regualr Django application it is possible to configure tasks, jobs, backends, queues programmatically

We provide examples of this in the example_scripts/ directory, populate_analytics_automated.py gives and example of performing this.
models.py explains the database schema and the the fields that users can set.

Yaml upload and download
^^^^^^^^^^^^^^^^^^^^^^^^

If programmatic or web access is not suitable, it is also possible to dump the
job configurations to yaml or upload new configuration. You can write or edit
valid yaml for the database to configure jobs and tasks. The following URIs
provide this functionality

::

  http://127.0.0.1:8000/admin/dump
  http://127.0.0.1:8000/admin/load

Adding new celery queues
^^^^^^^^^^^^^^^^^^^^^^^^

A_A uses Celery to execute tasks. By default we provide a number of queues
that tasks can be assigned to. You can use the Queues admin pages to create
new ones. By default you can find 'localhost' and 'gridengine' name queues.

Internally these create 3 queues for each named, 'low\_localhost', 'localhost'
and 'high\_localhost'. These allow you to have queues that run with tasks
with different prioriies. By default jobs will be sent to the 'localhost' queue,
users who exceed the QUEUE_HOG_SIZE will have their jobs sent to the 'low\_' queue
and users who are logged in can be assigned to the 'high\_' queue.

Now if you deploy fewer workers listening to the 'low\_' queue those users
will be able to have jobs executed but will not be able to monopolise the system
at the expense of other users. If you do not wish the queues to run with different
access to resources then have your celery workers listen to all queues.

You can create new queues for different worker pools using the Queue Type Admin
http://127.0.0.1:8000/admin/analytics_automated/queuetype/. You set a new name
which will name the celery queues (low\_[name], [name] and high\_[name]) and
you set an execution behaviour. Currently 2 execution behaviours are supported.
With 'localhost' set the workers will run the configured task as though it is
a unix commandlines instruction and execute it on the machine the worker is
running on. With 'GridEngine' set the worker will send the task
to a DRMAA compliant grid engine head node for execution. Not the RServe options
is temporarily not supported


Authentication and queue management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the standard Django users authentication tools the Admin can add users
and then distribute users names and passwords to thoses users. Using the
authentication and queue settings the admin can control access to the system.

* DEFAULT_JOB_PRIORITY : Priority submissions will run at (default 1)
* LOGGED_IN_JOB_PRIORITY : Priority submissions will run at (default 2)
* QUEUE_HOG_SIZE : Soft limit for concurrent user jobs
* QUEUE_HARD_LIMIT : Hard limit for concurrent user jobs

Jobs priority takes 4 values; None, 0, 1 and 2.  None will cause jobs to be
rejected. 0 will send jobs to the low_* queue, 1 will send jobs to the regular
queue and 2 will send jobs to the high_* queue. If users have more jobs
running than the QUEUE_HOG_SIZE then their next submission will have the
drecremented by one. If users have more jobs running than the QUEUE_HARD_LIMIT
then all future submission will be rejected.

If QUEUE_HOG_SIZE or QUEUE_HARD_LIMIT are set to None these values will
be ignored.

Code tasks
^^^^^^^^^^

If you have defined a queue with a R or Python execution behaviour then the
functionality of the Tasks which use these backends changes. Instead of
attempting to execute a commandline command these tasks will execute code.

When configuring a task you can now add R or Python code (as appropriate) in to
the Executable text area (you can resize this as appropriate).

There are a couple of quirks to note:

Things you can drop any arbitrarily large chunk of code in this box however
as debugging is none obvious you may want to constrain yourself to scripts
shorter than 100 lines.

A_A comes with Numpy and Scipy preinstalled so you can import those with out
having to call pip

R code calls will only work if r-base-dev has been installed as it is a
requirement of rpy2

Code is a dialect of R and Python as the " character is not valid. You must use
single quotes to delineate strings.
