.. _configurations_settings:

Configurations Settings
=======================

As A_A is a Django application it can be configured as per the usual Django
settings files. As it makes extensive use of Celery the celery settings
can also be further configured, see http://docs.celeryproject.org/en/latest/userguide/configuration.html

The following are important settings for A_A, these are marked by the comment
"# Required A_A user settings #" in the base.py settings files

::

  LOGGED_IN_JOB_PRIORITY: If a user is logged in choose which queue to send the job to (see above settings)
  QUEUE_HOG_SIZE: This is the number of concurrent jobs a user can submit before all following jobs are sent to the 'low_' priority queue
  QUEUE_HARD_LIMIT: This is the maximum number of concurrent jobs a user may submit. If set to 0 this means users can have unlimited jobs in the queue

A_A will email users if the Django email settings are configured, this is
as per the normal Django emailing but the following setings are required

::

  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'smtp.xx.xx.xx'
  EMAIL_PORT = 25
  EMAIL_HOST_USER = ''
  EMAIL_HOST_PASSWORD = ''
  DEFAULT_FROM_EMAIL = ''

A_A has 2 important email settings that configure the contents of the email
which is sent to users. You can customise the email subject and default
message with the following

::

  EMAIL_SUBJECT_STRING = 'A_A Job Completion'
  EMAIL_MESSAGE_STRING = 'Your analysis is complete.\nYou can retrieve the ' \
                       'results from http://localhost/analytics_automated/' \
                       'submission/'
