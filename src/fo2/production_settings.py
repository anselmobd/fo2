# -*- coding: utf-8 -*-

from .settings import *

from .db_password import DBPASS

DEBUG = False

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "tussor_fo2_production",
        'USER': "tussor_fo2",
        'PASSWORD': DBPASS,
    },
    'so': {  # Systextil Oficial
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'xe',
        'USER': 'systextil',
        'PASSWORD': 'oracle',
        'HOST': '192.168.1.93',
        'PORT': '1521',
    }
}
