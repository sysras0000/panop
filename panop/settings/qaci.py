from .base import *

INFORMIX_JAR_PATH = '/usr/bin/local/informix/jdbc/lib/ifxjdbc.jar'

MYSQL_JAR_PATH = ''

SQLSERVER_JAR_PATH = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'panop',
        'USER': 'scorecard',
        'PASSWORD': 'scorecard_development',
        'HOST': 'qaci01.wic.west.com',
        'PORT': '5433'
    }
}