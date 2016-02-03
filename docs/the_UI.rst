Building Jobs
=============

Configuring jobs is most easily accomplished with the user interface. It is
possible to do this programmatically and the A_A github account comes with a
python script, `populate_analytics_automated.py` which automatically configures
the job we'll walk through here.

First you need to define a **Backend** and a series of **Tasks** and then
these **Tasks** can be plugged together as a **Job**.

Assuming you correctly followed the dev installation instructions, you'll need
to log in by pointing your browser at http://127.0.0.1:8000/admin/ and log in
using the superuser details you set during installation.

Define a Backend
----------------

The first thing to do is to define the details for each **Backend** your
tasks will use. In the basic configuration we started only one set of workers
watching only the task queues for the LOCALHOST backend so we'll only configure
one LOCALHOST backend.

In the admin interface click on the Backends option and then click on the
"Add Backend" button. Fill out the form as per the screenshot below

.. image:: backend_config.png

**Name**: Gives your backend a useful memorable name

**Server Type**: Tells A_A what kind of execution location this is

**IP & Port**: When a backend is remote to the worker these details allow the worker
to find the backend on the network. These are not used for the LOCALHOST backend,
**NOTE: THESE ARE CURRENTLY NOT USED IN THIS RELEASE OF A_A**

**Path**: This is a location on a disk (or network drive) which the backend has access to
it will be used to store temporary files which the task needs on execution

**Backend Users**: You can define a user (user name and passowrd) which the worker
will use to execute the task on backend which support this functionality
(i.e. Hadoop, Grid Engine). This is ignored for other backend types.
**NOTE: LOGGING IN AND USER JOB PRIORITY IS NOT CURRENTLY SUPPORTED IN
THIS VERSION OF A_A**

Define a Task
-------------

Now we define 2 tasks. Return to the admin interface at http://127.0.0.1:8000/admin/.
Click on the Tasks link and then select "Add Task". Fill out the form as below.
We're going to define one task which list the temporary directory and sends the information
to a file. And a second task which will grep that file for certain lines. The output of
the grep will be available to the users.

**Task 1**

.. image:: task1.png

**Task 2**

.. image:: task2.png

**Name**: A useful memorable name for this task

**Backend**: The backend where this task will run, as defined above

**Description**: This allows you to enter a short description of the task.

**In Glob**: A comma separated list of file endings (i.e. .txt, .pdf, etc..)
If this task is the 1st in a job and needs to consume a user input file then
the file will be given a suffix using the first glob in the list. Note that the
1st file ending in this list will be used to created an internal file string of the format
JOB_UUID.[ENDING] this will be used interpolation in to the $INPUT control (see
below). If the task is not the first one in a job the remaining globs will
be used to retrieve all matching files from the previous task's results.

**Out Glob**: A comma separated list of file endings (i.e. .txt, .pdf, etc..)
This defines the file endings for all files that will be gathered up and
returned to the database when the task completes. Note that the 1st file ending in this
list will be used to created a file string of the format JOB_UUID.[ENDING] for
interpolation in to the $OUTPUT flag (see below)

**stdout glob**: If you wish to record the tasks stdout then you can provide a
file suffix. The task will now perform as though you had used a standard unix
file redirect.

**Executable**: This is the program the worker will execute with any default
flags and options. Using $INPUT and $OUTPUT allows you to insert
strings JOB_UUID.[1stInGlob] and JOB_UUID.[1stOutGlob] **NOTE THAT TO JUDGE A TASK SUCCESSFUL IT MUST RETURN A 0
EXIT STATUS (THIS WILL BE CHANGED IN THE FUTURE)**

Parameters
^^^^^^^^^^

The task params take one of two forms. Boolean valued (known as flags), or
non-boolean valued (known as options).

**Flag**: These are options which will be interpolated to the executable command

**Default**: This value is required if the flag in non-boolean

**Bool Valued**: Sets whether this is a boolean flag and therefore whether it
needs a default value

**REST Alias**: A short string which will identify the user's control of this option when they
call the REST api, i.e one of the POST params the user will need to pass

Executable Syntax
^^^^^^^^^^^^^^^^^
It is worth noting that tasks use the Python package commandRunner to execute
(https://pypi.python.org/pypi/commandRunner/). So it is worth reading those
docs for the API.

The executable line can be any arbitrarily long command line statement even
including ';' but it must not contain any redirection statements for stdout or
stderr. This commands, flags and options can contain one of the two control statements which will
be interpolated, neither of which are required.

**$INPUT**: The location of an input file using the first entry **In Glob**

**$OUTPUT**: The location of an input file using the first entry **Out Glob**

Command construction proceeds by first tokenising the Executable string. Any
parameters which are set are tokenised and inserted after the executable. Lastly
any instance of $INPUT, $OUTPUT are interpolated to the string and anything in
stdout is captured by default. The following example should explain::

    Job ID: f7a314fe
    Executable: "/usr/bin/testy -u 123 -la"
    Parameter1: "-z"
    Parameter2: "--in": "$INPUT"
    Parameter3: "--out": "$OUTPUT"
    Parameter4: "--score": 123
    in_glob: ".in"
    out_glob: ".out, .stdout"

Given these settings the following internal strings will be constructed
input_string: f7a314fe.in
output_string: f7a314fe.out
stdout_string: f7a314fe.stdout

The final command string will be constructed as::

    /usr/bin/testy -z --in f7a314fe.in --out f7a314fe.out -u 123 -la > f7a314fe.stdout

Note that flags come before options and any params set in the initial executable
string move to the end of the command. By default stdout is redirected to a file
ending with .stdout. In this example when the task when the task completes all
files ending with .out and .stdout will be returned to the database as results

Define a Job
------------

Now we have some tasks attached to a backend we can define a **Job**. Return to
http://127.0.0.1:8000/admin/ and click on Jobs then select "Add Job"

.. image:: job.png


**Name**: A useful name for the job. Users will use this when submitting data
to the API

**Runnable**: Whether the user can call this job (**NOT YET IMPLEMENTED**)

Validators
^^^^^^^^^^

You can set one or more data validators for the jobs. Regular expressions will
examine the contents of the incoming file of data to ensure that you they match.

**Validation Type**: This is the type of validation the incoming data must pass
in the :ref:`advanced_uses` tutorial we'll show you how to add custom validators
to this dropdown. **NOTE THAT BY DEFAULT ONLY REGULAR EXPRESSION VALIDATION IS
SUPPORTED**

**Re String**: If you selected 'Regular Expression' validation then you need to provide
a valid python regular expression.

Steps
^^^^^

Now you select which tasks will run in which order.

**Tasks**: use the drop down to select from your named tasks

**Ordering**: A numeric value which defines the order the tasks will run in
starting with the lowest value. These need not start from 0 and need not be
strictly consecutive numbers

Using Your Job
--------------

You have now defined your first job. Users can use it by making a multi-part form
POST request to http://127.0.0.1:8000/analytics_automated/submission and
passing all the correct values.

Users *must* at a minimum pass the following information in

**job**: The name of the job as defined in the **Job** form in this example 'job1'

**submission_name**: A string by which the user will remember thier submission

**email**: An email address (currently required even if A_A is not set to return emails)

For the job we defined each task had two params users must pass in values for these.
In this instance these had the REST alias of 'all' and 'number' and are identified
in the HTTP submission by having their task name and an underscore added

**task1_all**: When we defined with Parameter for task1 bool_valued was selected
the calling user must pass in True or False

**task2_number**: When we defined with Parameter for task2 bool_valued was *not*
selected. The user must pass in a string value, typically a number.

Checking what jobs are available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have defined some jobs the system provides a GET end point, `/endpoints`
which returns a list of all the valid jobs and their required params. You can
access this json at

http://127.0.0.1/endpoints/

Submitting Data
^^^^^^^^^^^^^^^

And example of using the api can be found in the `send_file.py` script.

When a submission is succesful the system returns a blob of json with a UUID.
Calling http://127.0.0.1:8000/analytics_automated/submission/[UUID] with a GET
request will return a json with the current state of the job.
