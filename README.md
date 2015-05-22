# automated_analytics
Middleware layer for exposing analytics and distributed computing jobs as web services

## Setup of automated analytics

1. Install latest python3.x
2. Install git
3. set up bashrc or bash_profile to point virtualevnwrapper at the correct
python 3. I added this to my .bash_profile

```PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
export PATH

VIRTUALENVWRAPPER_PYTHON='/Library/Frameworks/Python.framework/Versions/3.4/bin/python3'
export VIRTUALENVWRAPPER_PYTHON

source virtualenvwrapper.sh
```

4. `> source virtualenvwrapper.sh`
5. `> mkvirtualenv analytics_automated`
6. `> workon analytics_automated (discontect with deactivate)``
7. Install these libraries to this env
 * `> pip install django`
 * `> pip install setuptools`
 * `> pip install distribute`
 * `> pip install django`
 * `> pip install virtualenv`
 * `> pip install virtualenvwrapper`
 * `> pip install django-admin-bootstrapped`
 * `> pip install django-bootstrap3`

8. check out analytics_automated from git
