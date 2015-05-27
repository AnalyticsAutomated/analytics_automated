import json
import os
from django.core.exceptions import ImproperlyConfigured

from .base import *
try:
    from .dev_secrets import *
except ImportError as e:
    pass

SETTINGS_PATH = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(SETTINGS_PATH, 'dev_secrets.json')
with open(os.path.join(SECRETS_PATH)) as f: secrets = json.loads(f.read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'analytics_automated_db',
        'USER': get_secret("USER", secrets),
        'PASSWORD': get_secret("PASSWORD", secrets),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SECRET_KEY = get_secret("SECRET_KEY", secrets)


DEBUG = True
