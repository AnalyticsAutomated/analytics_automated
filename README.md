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
 * `> pip install django`
 * `> pip install setuptools`
 * `> pip install distribute`
 * `> pip install django`
 * `> pip install django-admin-bootstrapped`
 * `> pip install django-bootstrap3`
 * `> pip install Pillow`
 * `> pip install django-registration-redux`
 * `> pip install psycopg2`

9. Install postgres for your system, MacOS version can be found at
   http://www.postgresql.org/download/macosx/ the graphical installer is a
   good option for Mac.
10. Once configured add a postres user for analytics automated
 * `CREATE ROLE a_a_user WITH LOGIN PASSWORD 'thisisthedevelopmentpasswordguys';`
 * `GRANT ALL PRIVILEGES ON DATABASE analytics_automated_db TO a_a_user;`
 * `ALTER USER a_a_user CREATEDB;`
11. On Mac you probably have to link some psql bits (mind the version)
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libssl.1.0.0.dylib /usr/lib`
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libcrypto.1.0.0.dylib /usr/lib`
 * `sudo mv /usr/lib/libpq.5.dylib /usr/lib/libpq.5.dylib.old `
 * `sudo ln -s /Library/PostgreSQL/9.4/lib/libpq.5.dylib /usr/lib`
12. check out analytics_automated from git

TODO
====
1. Multiple settings
2. Move secrets to ENV settings?
3. Multiple requirements
4. add unipath to settings.py
5. Chapters six for timestamp abstract model
6. Look over the null and blank db settings as per chapter 6
7. Add tests for existing models and views
