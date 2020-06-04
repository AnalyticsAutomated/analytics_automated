.. _periodic_tasks:

Periodic Tasks
==============

Periodic Tasks are handled by Celery Beat. Starting the workers with the
--beat option will allow you to start the periodic task service. Remember
to start the separate beat daemon if running in production/staging modes.

This mode is still in beta and has not been fully tested

Most details can be found at

http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html

Analytics automated installs the django-celery-beat package so you can
use the A_A interface to configure periodic tasks rather than using the
settings files.

https://pypi.org/project/django_celery_beat/

To build a periodic job you should create a job as normal as described elsewhere
in these docs. Then, when setting a periodic task you must register the task as the
'analytics_automated.tasks.task_job_runner'. Further down the page set the
Interval or Crontab as per a celery beat instructions. In the arguments list
you must add the name of the job your wish to run. And lastly the
queue on which the job should run must be set. If you can create a new
'Queue Type' for periodic tasks but you must ensure you have started some
workers which as listening to that queue
