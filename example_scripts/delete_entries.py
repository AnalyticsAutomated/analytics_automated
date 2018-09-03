#
# Short script populates the database with some test/example data
#
#
import os
import sys
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
import django
sys.path.append('./')
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'analytics_automated_project.settings.dev')
django.setup()
from analytics_automated.models import Backend, Job, Task, Step
from analytics_automated.models import Parameter, Submission, Result
from analytics_automated.models import Validator, BackendUser, Message


def delete_old_entries():
    all_objects = Submission.objects.all()
    old_objects = Submission.objects.filter(
                          modified__lte=timezone.now()-timedelta(days=10)).delete()

# Start execution here!
if __name__ == '__main__':
    print("Starting A_A deletion script")
    delete_old_entries()


# source /home/django_aa/aa_env/bin/activate
# cd /home/django_aa/analytics_automated/
# python example_scripts/delete_entries.py
