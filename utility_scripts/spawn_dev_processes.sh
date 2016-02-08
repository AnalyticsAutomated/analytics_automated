#!/bin/bash

#possibly more the postmaster.pid if the machine rebooted
gnome-terminal --working-directory=/cs/research/bioinf/home1/green/dbuchan/Code/analytics_automated --tab -e 'sh -c "postmaster -D /scratch0/NOT_BACKED_UP/dbuchan/postgres"' --tab -e 'sh -c "sleep 2; rabbitmq-server"' --tab -e 'bash -c "export HISTFILE=~/Code/analytics_automated/utility_scripts/aa.hist; sleep 2; workon analytics_automated; python manage.py runserver --settings=analytics_automated_project.settings.dev; exec bash"' --tab -e 'bash -c "export HISTFILE=~/Code/analytics_automated/utility_scripts/aa.hist; sleep 2; workon analytics_automated; celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,celery; exec bash"'
