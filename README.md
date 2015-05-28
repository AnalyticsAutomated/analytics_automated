# automated_analytics
Middleware layer for exposing analytics and distributed computing jobs as web services

## Setup of automated analytics

1. Install latest python3.x
2. Install git
3. Install virtualenv and virtualenvwrapper
 * `> pip install virtualenv`
 * `> pip install virtualenvwrapper`
4. Set up bashrc or bash_profile to point virtualevnwrapper at the correct
python 3. I added this to my .bash_profile
    ```
    PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
    export PATH

    VIRTUALENVWRAPPER_PYTHON='/Library/Frameworks/Python.framework/Versions/3.4/bin/python3'
    export VIRTUALENVWRAPPER_PYTHON

    source virtualenvwrapper.sh
    ```
5. `> source virtualenvwrapper.sh`
6. `> mkvirtualenv analytics_automated`
7. `> workon analytics_automated (discontect with deactivate)`
8. Install these libraries to this env
 * `> pip install setuptools`
 * `> pip install distribute`

9. Install postgres for your system, MacOS version can be found at
   http://www.postgresql.org/download/macosx/ the graphical installer is a
   good option for Mac.
10. Once configured add a postgres user for analytics automated
 * `CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';`
 * `CREATE DATABASE analytics_automated_db;`
 * `GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;`
 * `ALTER USER a_a_user CREATEDB;`
11. On Mac you probably have to link some psql bits (mind the version)
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libssl.1.0.0.dylib /usr/lib`
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libcrypto.1.0.0.dylib /usr/lib`
 * `sudo mv /usr/lib/libpq.5.dylib /usr/lib/libpq.5.dylib.old `
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libpq.5.dylib /usr/lib`
12. Check out analytics_automated from git
13. Install the requirements from the relevant project requirements (probably requirements/dev.txt)
`pip install -r requirements/dev.txt`
14. Run the migrations (don't forget --settings=analytics_automated_project.settings.dev)
15. Start the server by defining the settings you are using
`python manage.py runserver --settings=analytics_automated_project.settings.dev`
16. Test the code also defining the settings you are using
`python manage.py test --settings=analytics_automated_project.settings.dev analytics_automated`

NEXT UP TODO
============
1. Django REST for Submission and results
  Submission : create and read, no external update and no external delete
  Result : create and read, no external update and no external delete
2. Submission view and tests.
3. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
