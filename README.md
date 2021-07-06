# analytics_automated

### Introduction:

Analytics Automated (A_A) is a 'lightweight' framework for automating long running
distributed computation principally focused on executing Data Science tasks.

Today it is trivially easy for Scientists, Researchers, Data Scientists and
Analysts to build statistical and predictive models. More often than not these
don't get turned in to useful and usable services; frequently becoming reports
on work which does not get actioned. In short, organisations often have trouble
operationalising the models and insights which emerge from complex statistical
research and data science

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

### Documentation

Full documentation can be found at https://analytics-automated.readthedocs.io/en/latest/

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

# Requirements

You will need

* python 3.6
* postgres 9.6
* Redis
* django
* celery


The full details for starting analytics_automated are set out in the documentation
at https://analytics-automated.readthedocs.io/en/latest/installation/


## Install the python packages

```pip install -r requirements/dev.txt
```

## create logs dir
```mkdir logs
```

## Install the postgres database and then start postgres

Export the path to wherever postgres has been installed.
For mac using homebrew this will be in /usr/local/Cellar
This should look something like:

```export PATH="/usr/local/Cellar/postgresql@9.6/9.6.20/bin/:$PATH"```

## start postgresql

```pg_ctl -D /usr/local/var/postgresql@9.6 -l /usr/local/var/postgresql@9.6/server.log start```

## login to the database and create a new database/user
```psql -h localhost -d postgres```

This will start the database server on your localhost. You can then go ahead and make a database with associated user.

### create a django db user for AA
```

CREATE DATABASE analytics_automated_db;

CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';

GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;

ALTER USER a_a_user CREATEDB;
```
## Now open a new terminal window and start redis working

```redis-server```

If redis is not installed you can do that using brew,yum or apt-get
You can check its operation using:

```ps aux | grep redis-server```

## Configure Django

```cd analytics_automated_project/settings
touch base_secrets.json
touch dev_secrets.json
```
add to analytics_automated_project/settings/dev_secrets.json

{
  "USER": "a_a_user",
  "PASSWORD": "thisisthedevelopmentpasswordguys",
  "SECRET_KEY": "VERY LONG KEY HERE"
}

add to base_secrets.json

{}


## Start celery
  You can now start the celery workers
  ```celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,low_R,R,high_R,low_Python,Python,high_Python
  ```

## Start the server
from within analytics_automated you can now make the migrations , add a superuser and start the runserver

```
python manage.py makemigrations --settings=analytics_automated_project.settings.dev
python manage.py migrate --settings=analytics_automated_project.settings.dev
```
```
python manage.py createsuperuser --settings=analytics_automated_project.settings.dev
```
You will be asked for a username and password - this will be the username/password you
use to log into the server.

python manage.py runserver --settings=analytics_automated_project.settings.dev
```






NEXT UP TODO/REMINDERS
======================

1. On Submission delete propagate message to workers to kill task
2. Non-linear jobs (i.e tasks with multiple parents, full DAG support), see CWL support
3. Add CWL support to configure and dump tasks/jobs. Consider importing
   Toil library to handle parsing the yaml and pushing the results to the db
4. Further backends, Octave, matlab, SAS
5. SVG graphs for job progress.

Missing
=======
1. Robust to task failure. Some types of exception should probably be tried again and some failures should propagate to the user, likely need to some way to let the users configure this in a task
http://agiliq.com/blog/2015/08/retrying-celery-failed-tasks/
http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying-a-task-if-something-fails
2. Let jobs run jobs as nested structures; this will be part of adding CWL support
