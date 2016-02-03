#!/bin/bash

gnome-terminal -x sh -c 'postmaster -D /scratch0/NOT_BACKED_UP/dbuchan/postgres'
#gnome-terminal -x sh -c '/usr/bin/pg_ctl start -l /scratch0/NOT_BACKED_UP/dbuchan/postgres/logfile -D /scratch0/NOT_BACKED_UP/dbuchan/postgres/'
sleep 2
gnome-terminal -x sh -c 'rabbitmq-server'
sleep 2
gnome-terminal --working-directory=/cs/research/bioinf/home1/green/dbuchan/Code/analytics_automated -x sh -c 'python manage.py runserver --settings=analytics_automated_project.settings.dev'
sleep 2
gnome-terminal --working-directory=/cs/research/bioinf/home1/green/dbuchan/Code/analytics_automated -x sh -c 'celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,celery'
