import json
import os

from unipath import Path

from .base import *

DEV_SECRETS_PATH = SETTINGS_PATH.child("dev_secrets.json")
with open(os.path.join(DEV_SECRETS_PATH)) as f: secrets = json.loads(f.read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'analytics_automated_db',
        'USER': get_secret("USER", secrets),
        'PASSWORD': get_secret("PASSWORD", secrets),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CORS_ORIGIN_WHITELIST = (
        '127.0.0.1:4000',
    )

SECRET_KEY = get_secret("SECRET_KEY", secrets)

DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': "/static/js/jquery.min.js",
}

# TODO: Change this for staging and production
MEDIA_URL = '/submissions/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'submissions')
STATIC_URL = '/static_dev/'
# Change the test runner
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.cs.ucl.ac.uk'
EMAIL_PORT = '25'
# EMAIL_HOST_USER = 'psipred@cs.ucl.ac.uk'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'psipred@cs.ucl.ac.uk'
