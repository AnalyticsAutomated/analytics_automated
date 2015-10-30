TODO
====

1. RServe support

2. Add scheduled tasks
3. Non-linear jobs (i.e tasks with multiple parents)

Production things
-----------------

1. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

    enable app.Task.track_started
    Autoscaling

2. Consider Flower for celery monitoring
3. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
4. Investigate cached_property
