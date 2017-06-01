# -*- coding: utf-8 -*-

from .settings import *

from .db_password import DBPASS

DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "tussor_fo2_production",
        'USER': "tussor_fo2",
        'PASSWORD': DBPASS,
    }
}

