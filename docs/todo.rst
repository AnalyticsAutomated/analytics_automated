TODO
====

1. Raw RServe support
2. Job DAG visualisations
3. Authenticate users for priority running, setting to toggle sending logged
   in jobs or not.
4. Add scheduled tasks, just use celery???
5. Non-linear jobs (i.e tasks with multiple parents)
6. HADOOP/Spark?
7. Raw Python support

Production things
-----------------

1. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

    enable app.Task.track_started
    Autoscaling

2. Consider Flower for celery monitoring
3. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
4. Investigate cached_property
5. Config GridEngine users with different priorities
6. Config GridEngine with multiple submit hosts.
7. CI? Jenkins/Travis
