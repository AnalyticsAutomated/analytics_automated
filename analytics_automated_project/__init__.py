from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
from django.core import serializers

__all__ = ['celery_app']
