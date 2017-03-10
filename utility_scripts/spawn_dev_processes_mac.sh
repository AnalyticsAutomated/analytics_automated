#!/bin/bash
osascript -e 'tell application "Terminal"' -e 'do script with command "redis-server"' -e 'end tell'
osascript -e 'tell application "Terminal"' -e 'do script with command "workon analytics_automated; cd ~/Code/analytics_automated; python manage.py runserver --settings=analytics_automated_project.settings.dev"' -e 'end tell'
osascript -e 'tell application "Terminal"' -e 'do script with command "workon analytics_automated; cd ~/Code/analytics_automated; celery --app=analytics_automated_project.celery:app worker --loglevel=INFO -Q low_localhost,localhost,high_localhost,low_GridEngine,GridEngine,high_GridEngine,low_R,R,high_R,low_Python,Python,high_Python"' -e 'end tell'
