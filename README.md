# automated_analytics
Middleware layer for exposing analytics and distributed computing jobs as web services

## Setup of automated analytics

###Setup for a Mac which you control:

1. Install latest python3.x
2. Install git
3. Install RabbitMQ (configuring this may hose your postgres install on OSX, so
  install RabbitMQ before postgres)

 `http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#installing-rabbitmq-on-os-x`
4. Install postgres for your system, MacOSX version can be found at
 `brew install postgres`
5. Install virtualenv and virtualenvwrapper
 * `> pip install virtualenv`
 * `> pip install virtualenvwrapper`
6. Set up bashrc or bash_profile to point virtualevnwrapper at the correct
python 3. I added this to my .bash_profile
    ```
    PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
    export PATH

    VIRTUALENVWRAPPER_PYTHON='/Library/Frameworks/Python.framework/Versions/3.4/bin/python3'
    export VIRTUALENVWRAPPER_PYTHON

    source virtualenvwrapper.sh
    ```
Then run

`> source virtualenvwrapper.sh`
7. `> mkvirtualenv analytics_automated`
8. `> workon analytics_automated` (FYI discontect with deactivate)
9. Install these libraries to this env
 * `> pip install setuptools`
 * `> pip install distribute`
10. Once configured log in to postgres (psql) and add a postgres user for analytics automated
 * `CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';`
 * `CREATE DATABASE analytics_automated_db;`
 * `GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;`
 * `ALTER USER a_a_user CREATEDB;`
11. On Mac you probably have to link some psql bits (mind the version)
 * `sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libssl.1.0.0.dylib /usr/lib`
 * `sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libcrypto.1.0.0.dylib /usr/lib`
 * `sudo mv /usr/lib/libpq.5.dylib /usr/lib/libpq.5.dylib.old `
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libpq.5.dylib /usr/lib`
12. Check out analytics_automated from git

`git clone https://github.com/AnalyticsAutomated/analytics_automated.git`
13. Install Celery
`pip install celery`
14. Install the AnalyticsAutomated requirements from the relevant project requirements (probably requirements/dev.txt)
`pip install -r requirements/dev.txt`
15. add some configuration bits which are omitted from github
 * `cd analytics_automated_project/settings/`
 * `touch base_secrets.json`
 * `touch dev_secrets.json`
16. Add the BUGSNAG key to base_secrets.json as per

`{
  "BUGSNAG": ""
 }`

17. Add the dev database and secret key to the dev_secrets.json as per

`{
  "USER": "a_a_user",
  "PASSWORD": "thisisthedevelopmentpasswordguys",
  "SECRET_KEY": "SOME ABSURDLY LONG RANDOM STRING"
 }`

18. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev)and create and admin user for the project.

`python manage.py migrate --settings=analytics_automated_project.settings.dev`

19. Start the server by defining the settings you are using

`python manage.py runserver --settings=analytics_automated_project.settings.dev`

20. Test the code also defining the settings you are using

`python manage.py test --settings=analytics_automated_project.settings.dev analytics_automated`

###Setup for a linux machine on our network
1. Set yourself up so you're using bash rather than csh, this will make virtualenv much easier to deal with
2. Get your own python3, somewhere local rather than on the network
`/opt/Python/Python-3.4.1/bin/virtualenv [SOME_PATH]`
3. Add [SOME_PATH]/bin to your PATH in your .bashrc
4. Install virtualenv and virtualenvwrapper
 * `> pip install virtualenv`
 * `> pip install virtualenvwrapper`
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
  * `> pip install setuptools`
  * `> pip install distribute`
  * `> pip install celery`
7. Initialise postgres (you can add the path to PGDATA env var), this should
add a superuser with your user name
  * `> initdb -D [SOME_PATH]`
8. start postgres, You may additionally need to get /var/run/postgres made writeable by all to run this.
  * `> postgres -D [SOME_PATH] >logfile 2>&1 &`
  or
  * `pg_ctl start -l logfile`
  You can no log in with
  * `psql -h localhost -d postgres`
9. Once configured add a postgres user for analytics automated
 * `CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';`
 * `CREATE DATABASE analytics_automated_db;`
 * `GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;`
 * `ALTER USER a_a_user CREATEDB;`
10. Install Erlang somewhere local (configure --prefix=[LOCAL DIR]). Don't forget to add this location to your PATH
 `http://www.erlang.org/download.html`
 `http://www.erlang.org/doc/installation_guide/INSTALL.htm`
10. Install RabbitMQ (configuring this may hose your postgres install on OSX, so
  install RabbitMQ before postgres)
 `https://www.rabbitmq.com/install-generic-unix.html`
11. Check out analytics_automated from git
`git clone https://github.com/AnalyticsAutomated/analytics_automated.git`
12. Install Celery
`pip install celery`
13. Install the requirements from the relevant project requirements (probably requirements/dev.txt)
`pip install -r requirements/dev.txt`
14. add some configuration bits which are omitted from github
 * `cd analytics_automated_project/settings/`
 * `touch base_secrets.json`
 * `touch dev_secrets.json`
15. Add the BUGSNAG key to base_secrets.json as per
`{
  "BUGSNAG": ""
 }`
16. Add the dev database and secret key to the dev_secrets.json as per
`{
  "USER": "a_a_user",
  "PASSWORD": "thisisthedevelopmentpasswordguys",
  "SECRET_KEY": "SOME ABSURDLY LONG RANDOM STRING"
 }`
17. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev) and create and admin user for the project.
18. Start the server by defining the settings you are using
`python manage.py runserver --settings=analytics_automated_project.settings.dev`


NEXT UP TODO
============
1. Django REST for Submission
  Submission : create and read, no external update and no external delete
2. REST return for results (create and read), create requires authentication?
3. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
4. Get Submission form validation to return more meaningful error state
