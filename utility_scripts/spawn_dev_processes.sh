#!/bin/bash

#possibly more the postmaster.pid if the machine rebooted
gnome-terminal --working-directory=/home/dbuchan/Code/analytics_automated --tab -- sh -c "postmaster -D /scratch/postgres_databases"
gnome-terminal --working-directory=/home/dbuchan/Code/analytics_automated --tab -- sh -c "sleep 2; redis-server;"
gnome-terminal --working-directory=/home/dbuchan/Code/analytics_automated --tab -- bash --rcfile ~/.bashrc -c "export HISTFILE=~/Code/analytics_automated/utility_scripts/aa.hist; source  virtualenvwrapper.sh; sleep 2; workon analytics_automated; python manage.py runserver --settings=analytics_automated_project.settings.dev; exec bash"
gnome-terminal --working-directory=/home/dbuchan/Code/analytics_automated --tab -- bash -c "export HISTFILE=~/Code/analytics_automated/utility_scripts/aa.hist; source  virtualenvwrapper.sh; sleep 2; workon analytics_automated; celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,low_GridEngine,GridEngine,high_GridEngine,low_R,R,high_R,low_Python,Python,high_Python; exec bash"
