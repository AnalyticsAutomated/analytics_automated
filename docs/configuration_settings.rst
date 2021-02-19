.. _configurations_settings:

Configurations Settings
=======================

As A_A is a Django application it can be configured as per the usual Django
settings files. As it makes extensive use of Celery the celery settings
can also be further configured, see http://docs.celeryproject.org/en/latest/userguide/configuration.html

We recommend people adminstering this system be familiar with both Django and
Celery application deployment. The following are important settings for A_A,
these are marked by the comment "# Required A_A user settings #" in the base.py
settings files

::

  QUEUE_HOG_SIZE: This is the number of concurrent jobs a user can submit before all following jobs are sent to the 'low_' priority queue
  QUEUE_HARD_LIMIT: This is the maximum number of concurrent jobs a user may submit. If set to 0 this means users can have unlimited jobs in the queue
  LOGGED_IN_JOB_PRIORITY: If a user is logged in choose which queue to send the job to (see above settings), this setting is currently not supported

A_A will email users if the Django email settings are configured, this is
as per the normal Django emailing but the following setings are required.
You can also set whether a user's email should be stored or deleted. An
administrator's email address for alerting when periodic tasks are done
and a default sending email address must be provide

::

  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'smtp.xx.xx.xx'
  EMAIL_PORT = 25
  EMAIL_HOST_USER = ''
  EMAIL_HOST_PASSWORD = ''
  DEFAULT_FROM_EMAIL = ''
  EMAIL_DELETE_AFTER_USE = True
  ADMIN_EMAIL = ""
  DEFAULT_FROM_EMAIL = ''

A_A has 2 important email settings that configure the contents of the email
which is sent to users. You can customise the email subject and default
message with the following

::

  EMAIL_SUBJECT_STRING = 'A_A Job Completion'
  EMAIL_MESSAGE_STRING = 'Your analysis is complete.\nYou can retrieve the ' \
                       'results from http://localhost/analytics_automated/' \
                       'submission/'


Job running priority is handled with the following settings. Default priority
is 1. 2 is high priority and usually reserved for logged in users. Submission
limits are handled by the queue size. QUEUE_HOG_SIZE is the number of running
jobs a user can have before further jobs are sent to workers that handle
the LOW priority queue. HARD_LIMIT sets the total number of jobs a user can
submit. Setting either to 0 sets ignores these settings.

::

  DEFAULT_JOB_PRIORITY = 1
  LOGGED_IN_JOB_PRIORITY = 2
  QUEUE_HOG_SIZE = 10
  QUEUE_HARD_LIMIT = 15

As the system use celery the workers and queue can be configured very finely.
The minimum set of celery settings needed are below and further details can
be found in the celery docs (http://www.celeryproject.org/)

::

  CELERY_BROKER_URL = "redis://localhost:6379/0"
  CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
  CELERY_TIMEZONE = 'Europe/London'

When running in production or in a distributed fashion you should ensure the
CORS whitelist is correctly set.

::

  CORS_ORIGIN_WHITELIST = (
          '127.0.0.1:4000',
          '127.0.0.1:8000',
      )

If running in dev mode ensure the development settings are correctly set

::

  DEBUG = True
  INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
  DEBUG_TOOLBAR_CONFIG = {
      'JQUERY_URL': "/static/js/jquery.min.js",
  }
  MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']
