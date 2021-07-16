"""
WSGI config for analytics_automated_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import logging
import sys
logging.basicConfig(stream=sys.stderr)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analytics_automated_project.settings.production")

application = get_wsgi_application()
