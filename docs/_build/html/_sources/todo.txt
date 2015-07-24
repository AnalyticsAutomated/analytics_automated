TODO
====

1. Add endpoint which returns all the public operations/jobs
2. Grid Engine support
3. RServe support

4. Is it worth adding types to vars for clarity?

5. Add scheduled tasks
6. Non-linear jobs (i.e tasks with multiple parents)

Production things
-----------------

1. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

    enable app.Task.track_started
    Autoscaling

2. Solution for file storage in staging/production???
3. Consider Flower for celery monitoring
4. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
5. Investigate cached_property
