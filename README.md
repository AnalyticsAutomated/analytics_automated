# analytics_automated

Current state: Release Candidate 1.0

### Before You Go Much further

We have yet to deploy this in anger ourselves. You are downloading and using
this at your own risk

### Continue:

Analytics Automated (A_A) is a lightweight framework for automating long running
distributed computation principally focused on executing Data Science tasks.

Today it is trivially easy for Scientists, Researchers, Data Scientists and
Analysts to build statistical and predictive models. More often than not these
don't get turned in to useful and usable services; frequently becoming reports
on work which does not get actioned. In short, organisations often have trouble
operationalising the models and insights which emerge from complex statistical
research and data science.

Analytics automated is targeted at streamlining the process for turning your
predictive software into usable and maintainable services.

With A_A Researchers and data scientists can build models in the modelling tool
of their choice and then, with trivial configuration, Analytics Automated will
turn these models in to an easy to use API for integration in to websites and
other tools.

The other principal benefit of this system is to reduce technology lock-in.
Statistical modelling and Data Science expertise is now spread across a wide
range of technologies (Hadoop, SAS, R and more) and such technological
proliferation shows no sign of slowing down. Picking a single modeling
technology greatly reduces the pool of possible employees for your organisation
and backing the "wrong horse" means if you have to change it can be very costly
in terms of time, staffing and money.

A_A is agnostic to the modeling software and technologies you choose to build
your group around.

### How it works

Users send data as a REST POST request call to a pre-configured analysis or
prediction task and after some asynchronous processing they can come back and
GET their results. It's as simple as that and you are free to build this in
to any system you have or build the UI of your choice.

### Roadmap

1. Allows users to configure computational jobs and run them in a distributed
fashion  - DONE
2. Allow jobs to run in R, Grid Engine and Hadoop - Next Up
3. add further backends; Octave, matlab,

# Requirements

You will need

* python3
* postgres
* rabbitmq
* django
* celery

NEXT UP TODO/REMINDERS
======================

1. Add endpoint which returns all the public operations
2. Grid Engine support
3. RServe support

4. Is it worth adding types to vars for clarity?

5. Add scheduled tasks
6. Non-linear jobs (i.e tasks with multiple parents)

Production things:

2. Celery for workers https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

    enable app.Task.track_started
    Autoscaling

3. Solution for file storage in staging/production???
4. Consider Flower for celery monitoring
5. Security https, and authentication, HSTS????, allowed hosts for A_A,26.12.2 (ensure we have text files with no code in)
5. Investigate cached_property
