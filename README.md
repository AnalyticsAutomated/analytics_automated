# automated_analytics
Middleware layer for exposing analytics and distributed computing jobs as web services

## Setup of automated analytics

If we're starting from scratch you will need to install the following:
order.

1. Install latest python3.x
2. Install git
3. Install RabbitMQ (configuring this may hose your postgres install, so
  install RabbitMQ before postgres)
 `http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#installing-rabbitmq-on-os-x`
4. Install postgres for your system, MacOS version can be found at
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
7. `> source virtualenvwrapper.sh`
8. `> mkvirtualenv analytics_automated`
9. `> workon analytics_automated (discontect with deactivate)`
10. Install these libraries to this env
 * `> pip install setuptools`
 * `> pip install distribute`
11. Once configured add a postgres user for analytics automated
 * `CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';`
 * `CREATE DATABASE analytics_automated_db;`
 * `GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;`
 * `ALTER USER a_a_user CREATEDB;`
12. On Mac you probably have to link some psql bits (mind the version)
 * `sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libssl.1.0.0.dylib /usr/lib`
 * `sudo ln -s /usr/local/Cellar/openssl/1.0.2a-1/lib/libcrypto.1.0.0.dylib /usr/lib`
 * `sudo mv /usr/lib/libpq.5.dylib /usr/lib/libpq.5.dylib.old `
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libpq.5.dylib /usr/lib`
13. Check out analytics_automated from git
14. Install Celery
`pip install celery`
15. Install the requirements from the relevant project requirements (probably requirements/dev.txt)
`pip install -r requirements/dev.txt`
16. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev)
17. Start the server by defining the settings you are using
`python manage.py runserver --settings=analytics_automated_project.settings.dev`
18. Test the code also defining the settings you are using
`python manage.py test --settings=analytics_automated_project.settings.dev analytics_automated`

NEXT UP TODO
============
1. Django REST for Submission and results
  Submission : create and read, no external update and no external delete
  Result : create and read, no external update and no external delete
2. Add UUID index for submission and index for job name
3. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
