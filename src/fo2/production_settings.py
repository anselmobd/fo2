# -*- coding: utf-8 -*-

from .settings import *

from .db_password import (
    DBPASS,
    DBPASS_SO,
    DBPASS_PERSONA,
    DBPASS_F1,
    DBPASS_SH,
)

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
        'PASSWORD': DBPASS_SO,
        'HOST': '192.168.1.28',
        'PORT': '1521',
    },
    'sn': {  # Systextil OC (nuvem)
        'ENGINE': 'django.db.backends.oracle',
        # 'NAME': '10.0.0.3:1521/db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        'NAME': '152.67.55.216:1521/db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        'USER': 'systextil',
        'PASSWORD': DBPASS_SH,
    },
    'persona': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nasajon_db3_20200617_163619",
        'USER': "postgres",
        'PASSWORD': DBPASS_PERSONA,
        'HOST': '192.168.1.96',
        'PORT': '5432',
    },
}

DATABASES_EXTRAS = {
    'f1': {  # F1 e SCC
        'ENGINE': 'firebird',
        'NAME': '/dados/db/f1/f1.cdb',
        'USER': 'sysdba',
        'PASSWORD': DBPASS_F1,
        # 'HOST': 'localhost',
        # 'PORT': 13050,
        'HOST': '192.168.1.98',
        'PORT': 3050,
        'OPTIONS': {'charset': 'WIN1252'},
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'AUTOCOMMIT': None,
        'DIALECT': 3,
    },
    'sh': {  # Systextil homologação
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        'USER': 'systextil',
        'PASSWORD': DBPASS_SH,
        'HOST': '10.0.0.3',
        'PORT': '1521',
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "KEY_PREFIX": "FO2K",
        'TIMEOUT': 600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "20cTt21PwZZ1MmoiIOZi4vLzhk3JSmMwua0SERib"
                        "00Dtt3wAavSjhmzh03+GO+5OPFWRorvVaX8SQIBr",
        },
    }
}

MIKROTIK = {
    'user': 'apoioerp',
    'key_file': '/home/fo2_production/.ssh/id_rsa_tussor',
}
