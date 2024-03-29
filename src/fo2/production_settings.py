from .settings import *


DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

DEBUG_CURSOR_EXECUTE_PRT = False

DATABASES = {
    'default': {
        'ENGINE': DB_default_ENGINE,
        'HOST': DB_default_HOST,
        'PORT': DB_default_PORT,
        'USER': DB_default_USER,
        'PASSWORD': DB_default_PASSWORD,
        'NAME': DB_default_NAME,
    },
    'systextil_log': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "tussor_systextil_log",
        'USER': "tussor_fo2",
        'PASSWORD': DBPASS_STLOG,
        'HOST': '192.168.1.84',
        'PORT': '5432',
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
        'NAME': "nasajon_db",
        'USER': "postgres",
        'PASSWORD': DBPASS_PERSONA,
        'HOST': '192.168.1.84',
        'PORT': '5432',
    },
}

DATABASES_EXTRAS = {
    'f1': {  # F1 e SCC
        'ENGINE': 'firebird',
        'NAME': '/dados/db/f1/f1.cdb',
        'USER': 'sysdba',
        'PASSWORD': DBPASS_F1,
        'HOST': '192.168.1.98',
        'PORT': 3050,
        'OPTIONS': {'charset': 'WIN1252'},
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'AUTOCOMMIT': None,
        'DIALECT': 3,
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
