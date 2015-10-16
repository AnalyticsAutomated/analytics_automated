"""
Django settings for analytics_automated_project project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json
import bugsnag
import sys

from unipath import Path

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured


def get_secret(setting, secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
BASE_DIR = Path(__file__).ancestor(3)
TEMPLATE_PATH = BASE_DIR.child("templates")
STATIC_PATH = BASE_DIR.child("static")
STATIC_ROOT = BASE_DIR.child("static_root")
SETTINGS_PATH = Path(__file__).ancestor(1)

BASE_SECRETS_PATH = SETTINGS_PATH.child("base_secrets.json")
with open(os.path.join(BASE_SECRETS_PATH)) as \
    f: base_secrets = json.loads(f.read())

##############################
# Required A_A user settings #
##############################

DEFAULT_JOB_PRIORITY = 'MEDIUM'
LOGGED_IN_JOB_PRIORITY = 'HIGH'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.cs.ucl.ac.uk'
# EMAIL_PORT = ''
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# DEFAULT_FROM_EMAIL = ''
EMAIL_SUBJECT_STRING = 'A_A Job Completion'
EMAIL_MESSAGE_STRING = 'Your analysis is complete.\nYou can retrieve the ' \
                       'results from http://localhost/analytics_automated/' \
                       'submission/'

# Celery Settings
# BROKER_URL = ''
# CELERY_RESULT_BACKEND = ''  # This will be the postgresDB
# CELERY_TIMEZONE = 'Europe/London'
# CELERY_ENABLE_UTC = True
# CELERYD_MAX_TASKS_PER_CHILD = 100
# CELERYD_PREFETCH_MULTIPLIER = 1
# Uncomment to allow celery tests to run
# TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

# MEDIA_URL = '/submissions/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'submissions')

# DATABASES = {
#     'default': {
#         'ENGINE': '',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }
#
# SECRET_KEY = ''

########################
# End of User settings #
########################

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytics_automated',
    'rest_framework',
    'djcelery'
)

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.BrowsableAPIRenderer',
                                 'rest_framework.renderers.JSONRenderer',
                                 'rest_framework_xml.renderers.XMLRenderer',
                                 ),
    'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',
                               'rest_framework_xml.parsers.XMLParser',
                               ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'bugsnag.django.middleware.BugsnagMiddleware'
)

# # TODO: can't use this, api key only read from env
# BUGSNAG = {
#     'api_key': get_secret("BUGSNAG", base_secrets),
#     'project_root': BASE_DIR,
# }

ROOT_URLCONF = 'analytics_automated_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_PATH],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# redirect on  login
LOGIN_REDIRECT_URL = '/'

WSGI_APPLICATION = 'analytics_automated_project.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_PATH, ]


# Add bits for bootstrap 3 and message bits
DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'
MESSAGE_TAGS = {
            messages.SUCCESS: 'alert-success success',
            messages.WARNING: 'alert-warning warning',
            messages.ERROR: 'alert-danger error'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,  # 10 Megs
            'backupCount': 5,
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,  # 10 Megs
            'backupCount': 5,
            'filename': 'logs/django_request.log',
            'formatter': 'verbose',
        },
        'production': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/production.log',
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug', 'production', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
