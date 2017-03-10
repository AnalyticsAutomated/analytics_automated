.. _installation:

Basic Installation
==================

This guide will take you through setting up A_A in development mode. Analytics
automated is a Django application and has a couple of required dependencies

* Python3
* postgreSQL
* Redis
* Celery 4.x
* Django >1.10

Code Dependancies
-----------------

1. Get Python 3
^^^^^^^^^^^^^^^
You may also wish to sort out virtualenv and run the application within that, however that is beyond the scope of this installation guide

::

  https://www.python.org/downloads/

2. Install postgreSQL
^^^^^^^^^^^^^^^^^^^^^
If you're on a mac we advise using brew

::

  brew install postgres

If you're in a linux env some manner of

::

  yum install postgres

or

::

  apt-get install postgres

3. Install Redis
^^^^^^^^^^^^^^^^
One of

::

  brew install redis

  yum install redis

  apt-get install redis

4. Get the Analytics Automated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  git clone https://github.com/AnalyticsAutomated/analytics_automated.git

This will place the code in a dir called `analytics_automated/`

5. Install the python packages needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    cd analytics_automated/
    pip install -r requirements/dev.txt

Pre-launch configuration
------------------------
1. Set Up Postgres
^^^^^^^^^^^^^^^^^^
You need to setup some bits and pieces in postgres before we start

* You may need to initialise postgres::

    initdb -D [SOME_PATH]

* Start the postgres daemon::

    pg_ctl start -l /scratch0/NOT_BACKED_UP/dbuchan/postgres/logfile -D scratch0/NOT_BACKED_UP/dbuchan/postgres/

* Then login::

    psql -h localhost -d postgres

* Now create the django db user for A_A

  .. code-block:: sql

    CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';
    CREATE DATABASE analytics_automated_db;
    GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;
    ALTER USER a_a_user CREATEDB;

2. Now configure Django
^^^^^^^^^^^^^^^^^^^^^^^
We maintain the idea of separate secrets files which only you have control of. You need to create these and populate them.
base_secrets.json are site wide settings which dev and production will use.
dev_secrets.json are settings which only the dev installation will will access.
A production system will need a production_secrets.json

* Create the files we need::

    cd analytics_automated_project/settings
    touch base_secrets.json`
    touch dev_secrets.json`

* If you're using bugsnag add your bugsnag key to base_secrets.json::

    {
      "BUGSNAG": "YOUR KEY HERE"
    }

* Add the dev_secrets.json settings needed to start in developments mode. The postgres login credentials and the secret key::

    {
      "USER": "a_a_user",
      "PASSWORD": "thisisthedevelopmentpasswordguys",
      "SECRET_KEY": "VERY LONG KEY HERE"
    }

* Next open the base settings files in `analytics_automated_project/settings/base.py`
  In here you'll find a section at the top labelled "Required A_A user settings".
  These are all the things you need set for the app to run. We prefer to keep
  theses settings in dev.py and production.py files. Then we can start the server
  in different configs for different purposes.
  Either uncomment all these in base.py or move them to dev.py or production.py and
  set them there. You can leave the smtp settings commented if you do not wish to
  send alerts via email to your users.

3. Starting A_A in development localhost mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Start Redis::

    redis-server

* Start the celery workers, from the root dir of A_A. Note that we have to specify
  the queues the workers read from (-Q), for the basic settings we'll have
  these workers just watch all the default queueus, note that the
  workers are watching the low priority, normal priority and high priority.
  In a more complex set up you can have different worker pools on different
  machines watch specific queues.
  localhost queues::

    cd analytics_automated/
    celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,low_GridEngine,GridEngine,high_GridEngine,low_R,R,high_R,low_Python,Python,high_Python

* Run the Django migrations to configure the database::

    cd analytics_automated/
    python manage.py migrate --settings=analytics_automated_project.settings.dev

* Add an admin user to the Django application::

    cd analytics_automated/
    python manage.py createsuperuser

* Now start A_A, again from the root dir of the app. Note we'll start it assuming
  you put the users settings in settings/dev.py::

    cd analytics_automated/
    python manage.py runserver --settings=analytics_automated_project.settings.dev


4. Config complete
^^^^^^^^^^^^^^^^^^
   You should now be running all the components of A_A on a single machine with
   a set of workers watching the localhost queue. This means we can now configure
   data analysis pipelines which run code on the machine which the workers are running on.
   This is the most basic setup we can run Redis, the web app, the database and the workers
   on completely separate machines and even run multiple instances of the workers watching
   the same queue. We'll deal with this set in the :ref:`advanced_uses` tutorial.

5. Now move on to :ref:`how_it_works`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
