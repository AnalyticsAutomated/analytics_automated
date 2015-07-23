Installation
============

This guide will take you through setting up A_A in development mode. Analytics
automated is a Django application and has a couple of required dependencies

* Python3
* postgreSQL
* Erlang
* rabbitMQ
* Celery
* django 1.8

Code Dependancies
-----------------

1. Get Python 3. You may also wish to sort out virtualenv and run the application
within that, however that is beyond the scope of this installation guide::

    https://www.python.org/download/releases/3.0/

2. Install postgreSQL.

If you're on a mac we advise using brew::

    brew install postgres

If you're in a linux env some manner of::

    yum install postgres

or::

    apt-get install postgres

3. Erlang, rabbitMQ requires this, you may not have it installed and compiled. It's
available via

    http://www.erlang.org/download.html

    http://www.erlang.org/doc/installation_guide/INSTALL.htm

4. RabbitMQ, the message queue that the app and celery use

    https://www.rabbitmq.com/install-generic-unix.html

5. Get the A_A code from github::

    > git clone https://github.com/AnalyticsAutomated/analytics_automated.git

This will place the code in a dir called `analytics_automated/`

6. Install the python packages needed::

    > cd analytics_automated/
    > pip install -r requirements/dev.txt

Pre-launch configuration
------------------------

1. You need to setup some bits and pieces in postgres before we start::

  * You may need to initialise postgres::

      > initdb -D [SOME_PATH

  * Start the postgres daemon::

      > pg_ctl start -l /scratch0/NOT_BACKED_UP/dbuchan/postgres/logfile

  * Then login::

      > psql -h localhost -d postgres

  * Now create the django db user for A_A

.. code-block:: sql

      CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';
      CREATE DATABASE analytics_automated_db;
      GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;
      ALTER USER a_a_user CREATEDB;

2. Now configure Django. We maintain the idea of seperate secrets files
which only you have control of. You need to create these and populate them.
base_secrets.json at site wide settings which dev and production will use.
dev_secrets.json are settings which only the dev installation will will access.
A production system will need a production_secrets.json

  * Create the files we need::

      > cd analytics_automated/settings
      > touch base_secrets.json`
      > touch dev_secrets.json`

  * If you're using bugsnag add your bugsnag key to base_secrets.json

.. code-block:: json

      {
        "BUGSNAG": "YOUR KEY HERE"
      }

  * Add the dev_secrets.json settings needed to start in developments mode. The
    postgres login credentials and the secret key

      {
        "USER": "a_a_user",
        "PASSWORD": "thisisthedevelopmentpasswordguys",
        "SECRET_KEY": "VERY LONG KEY HERE"
      }
