#!/bin/bash
osascript -e 'tell application "Terminal"' -e 'do script with command "rabbitmq-server"' -e 'end tell'
osascript -e 'tell application "Terminal"' -e 'do script with command "workon analytics_automated; cd ~/Code/analytics_automated; python manage.py runserver --settings=analytics_automated_project.settings.dev"' -e 'end tell'
osascript -e 'tell application "Terminal"' -e 'do script with command "workon analytics_automated; cd ~/Code/analytics_automated; celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,celery"' -e 'end tell'
