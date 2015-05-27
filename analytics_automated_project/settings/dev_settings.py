
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'analytics_automated_db',
        'USER': 'a_a_user',
        'PASSWORD': 'thisisthedevelopmentpasswordguys',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SECRET_KEY = '=9hs%r&@r@@$#e%)!!^+7m4bkvob4yoxhq4h(eoufdpxu2=3+w'
