# analytics_automated

Current state: Embryonic

Middleware layer for exposing analytics and distributed computing jobs as web services.

It's easy for Scientists, Researchers, Data Scientists and analysts to build models but more often than not they don't get turned in to useful and usable services. This middleware is targeted at streamlining the process for turning predictive software into a service for users.

Essentially users can send data as a REST call to a pre-configured analysis or
prediction task and after some asynchronous processing they can come back and
get the results via REST. POSTing data and starting a worker is done. libraries
for the differing backends and the ability to GET results no yet implemented.

# Requirements

You will need

* python3
* postgres
* rabbitmq
* django
* celery

## Setup of analytics automated

Notes for our group members who may be less than familiar with setting up python
development environments.

###Setup for a Mac which you control:

1. Install latest python3.x
2. Install git
3. Install RabbitMQ (configuring this may hose your postgres install on OSX, so
  install RabbitMQ before postgres)
  * `http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#installing-rabbitmq-on-os-x`
4. Install postgres for your system, MacOSX version can be found at
   * `brew install postgres`
5. Install virtualenv and virtualenvwrapper

    ```
    > pip install virtualenv`
    > pip install virtualenvwrapper`
    ```
6. Set up bashrc or bash_profile to point virtualevnwrapper at the correct
python 3. I added this to my .bash_profile
    ```
    PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
    export PATH

    VIRTUALENVWRAPPER_PYTHON='/Library/Frameworks/Python.framework/Versions/3.4/bin/python3'
    export VIRTUALENVWRAPPER_PYTHON

    source virtualenvwrapper.sh
    ```
7. Then the following to start virtualenv wrapper and create and env

    ```
    > source virtualenvwrapper.sh
    > mkvirtualenv analytics_automated
    > workon analytics_automated (FYI discontect with deactivate)
    ```
8. Install these libraries to this env

    ```
    > pip install setuptools
    > pip install distribute
    ```
10. Once configured log in to postgres (psql) and add a postgres user for analytics automated

    ```
    CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';
    CREATE DATABASE analytics_automated_db;
    GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;
    ALTER USER a_a_user CREATEDB;
    ```
11. On Mac you probably have to link some psql bits (mind the version)

    ```
    > sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libssl.1.0.0.dylib /usr/lib
    > sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libcrypto.1.0.0.dylib /usr/lib
    > sudo mv /usr/lib/libpq.5.dylib /usr/lib/libpq.5.dylib.old
    > sudo ln -s /Library/PostgreSQL/9.4/lib/libpq.5.dylib /usr/lib
    ```
12. Check out analytics_automated from gitb
  * `> git clone https://github.com/AnalyticsAutomated/analytics_automated.git`
13. Install Celery
  * `> pip install celery`
14. Install the AnalyticsAutomated requirements from the relevant project requirements (probably requirements/dev.txt)
  * `> pip install -r requirements/dev.txt`
15. add some configuration bits which are omitted from github

    ```
    > cd analytics_automated_project/settings/
    > touch base_secrets.json
    > touch dev_secrets.json
    ```
16. Add the BUGSNAG key to base_secrets.json as per

    ```
    {
        "BUGSNAG": "YOUR KEY HERE"t
    }
    ```
17. Add the dev database and secret key to the dev_secrets.json as per

    ```
    {
      "USER": "a_a_user",
      "PASSWORD": "thisisthedevelopmentpasswordguys",
      "SECRET_KEY": "SOME ABSURDLY LONG RANDOM STRING"
    }
    ```
18. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev)and create and admin user for the project.
    * `> python manage.py migrate --settings=analytics_automated_project.settings.dev`
19. Start the server by defining the settings you are using
    * `> python manage.py runserver --settings=analytics_automated_project.settings.dev`
20. Test the code also defining the settings you are using
    * `> python manage.py test --settings=analytics_automated_project.settings.dev analytics_automated`

###Setup for a linux machine on our network
1. Set yourself up so you're using bash rather than csh, this will make virtualenv much easier to deal with
2. Get your own python3, somewhere local rather than on the network
  * `> /opt/Python/Python-3.4.1/bin/virtualenv [SOME_PATH]`
3. Add [SOME_PATH]/bin to your PATH in your .bashrc
4. Install virtualenv and virtualenvwrapper

    ```
    > pip install virtualenv`
    > pip install virtualenvwrapper`
    ```
5. Set up bashrc or bash_profile to point virtualevnwrapper at the correct
 python 3. I added all this to my .bash_profile
   ```
   export WORKON_HOME=/scratch0/NOT_BACKED_UP/dbuchan/virtualenvs
   export PROJECT_HOME=$HOME/Code
   VIRTUALENVWRAPPER_PYTHON='/scratch0/NOT_BACKED_UP/dbuchan/python3/bin/python3'
   export VIRTUALENVWRAPPER_PYTHON

   source virtualenvwrapper.sh

   ```
6. Install these libraries to this env

    ```
    > pip install setuptools
    > pip install distribute
    > pip install celery
    ```
7. Initialise postgres (you can add the path to PGDATA env var), this should
add a superuser with your user name
  * `> initdb -D [SOME_PATH]`
8. start postgres, You may additionally need to get /var/run/postgres made writeable by all to run this.
  * `> postgres -D [SOME_PATH] >logfile 2>&1 &`

  or

  * `> pg_ctl start -l /scratch0/NOT_BACKED_UP/dbuchan/postgres/logfile`

  You can now log in with
  * `> psql -h localhost -d postgres`
9. Once configured add a postgres user for analytics automated

    ```
    CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';
    CREATE DATABASE analytics_automated_db;
    GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;
    ALTER USER a_a_user CREATEDB;
    ```
10. Install Erlang somewhere local (configure --prefix=[LOCAL DIR]). Don't forget to add this location to your PATH
  * `http://www.erlang.org/download.html`
  * `http://www.erlang.org/doc/installation_guide/INSTALL.htm`
11. Install RabbitMQ
  * `https://www.rabbitmq.com/install-generic-unix.html`
12. Check out analytics_automated from git
  * `> git clone https://github.com/AnalyticsAutomated/analytics_automated.git`
13. Install Celery
  * `> pip install celery`
14. Install the requirements from the relevant project requirements (probably requirements/dev.txt)
  * `> pip install -r requirements/dev.txt`
15. add some configuration bits which are omitted from github

    ```
    > cd analytics_automated_project/settings/`
    > touch base_secrets.json`
    > touch dev_secrets.json`
    ```
16. Add the BUGSNAG key to base_secrets.json as per

    ```
    {
      "BUGSNAG": "YOUR KEY HERE"
    }
    ```
17. Add the dev database and secret key to the dev_secrets.json as per

    ```
    {
      "USER": "a_a_user",
      "PASSWORD": "thisisthedevelopmentpasswordguys",
      "SECRET_KEY": "SOME ABSURDLY LONG RANDOM STRING"
    }
    ```
18. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev)and create and admin user for the project.
    * `> python manage.py migrate --settings=analytics_automated_project.settings.dev`
19. Start the server by defining the settings you are using
    * `> python manage.py runserver --settings=analytics_automated_project.settings.dev`
20. Start RabbitMQ (making sure your path to erl is good)
    * `> rabbitmq-server start`
21. Get Celery going. You probably want to read something about celery and
django
http://michal.karzynski.pl/blog/2014/05/18/setting-up-an-asynchronous-task-queue-for-django-using-celery-redis/
For dev purposes we can start the workers with:
    * `> export PYTHONPATH=~/Code/analytics_automated/analytics_automated:$PYTHONPATH`
    * `> celery --app=analytics_automated_project.celery:app worker --loglevel=INFO`
21. Test the code also defining the settings you are using
    * `> python manage.py test --settings=analytics_automated_project.settings.dev`

NEXT UP TODO/REMINDERS
======================

Up next
1. Get submission RESULTS endpoint
2. Different Rabbit queues and workers for different backends
3. Authentication

Todo
2. REST return for results (create and read), create requires authentication?
3. Add endpoint which returns all the public operations
13. Convert task_runner submission updates to API calls to enable moving the
    workers to a different machine (i.e REST call to create results)

Production things
1. logrotate for logs
2. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
    enable app.Task.track_started

    Autoscaling
3. Solution for file storage in staging/production???
4. Consider Flower for celery monitoring
5. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
5. Investigate cached_property
