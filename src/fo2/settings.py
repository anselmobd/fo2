"""
Django settings for fo2 project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from . import __version__, __version__date__

from .db_password import DBPASS, DBPASS_PERSONA, DBPASS_F1


PROJ_VERSION = __version__
PROJ_VERSION_DATE = __version__date__

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '^2ms3ig21&-9lkk)-mb*@w5rp78or6g8##vrm16_l5rx%(*&dp'
with open(os.path.join(ROOT_DIR, 'etc/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # production
    'intranet', 'intranet.tussor', 'intranet.tussor.com.br', '192.168.1.96',
    'intranet.cuecasduomo.com.br', 'intranet.cuecasduomo.com', '177.23.138.90',
    '192.141.163.26', '192.141.163.25',
    # development
    '192.168.1.242', '192.168.1.225', 'localhost'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_tables2',
    # 'nested_inline',
    # Project
    'base',
    'comercial',
    'contabil',
    'geral',
    'insumo',
    'logistica',
    'lotes',
    'produto',
    'utils',
    'manutencao',
    'email_signature',
]

MIDDLEWARE = [
    # Cache
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # Others
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Project
    'utils.middlewares.LoggedInUserMiddleware',
    'utils.middlewares.NeedToLoginOrLocalMiddleware',  # N2LOL
    # Cache
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

N2LOL_REDIRECT = 'intranet'
N2LOL_ALLOWED_URLS = [
    '^/intranet/$',
    '^/accounts/login/.*$',
    '^/rh/.*$',
    '^/media/rh/.*$',
    '^/ack$',
]
N2LOL_ALLOWED_IP_BLOCKS = ['^192\.168\.1\..+$', '^127\.0\.0\.1$']

ROOT_URLCONF = 'fo2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "template"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                'geral.functions.get_list_geral_paineis',
            ],
        },
    },
]

SETTINGS_EXPORT = [
    'PROJ_VERSION',
    'PROJ_VERSION_DATE',
]

WSGI_APPLICATION = 'fo2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite3', 'db.sqlite3'),
        'TIME_ZONE': 'America/Sao_Paulo',
    },
    'so': {  # Systextil Oficial
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'xe',
        'USER': 'systextil',
        'PASSWORD': 'oracle',
        'HOST': 'localhost',
        'PORT': '28521',
    },
    'persona': {  # Nasajon
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nasajon_db",
        'USER': "nasajon_user",
        'PASSWORD': DBPASS_PERSONA,
        'HOST': 'localhost',
        'PORT': '25434',
    },
    'f1': {  # F1 e SCC
        'ENGINE': 'firebird',
        'NAME': '/dados/db/f1/f1.cdb',
        'USER': 'sysdba',
        'PASSWORD': DBPASS_F1,
        'HOST': 'localhost',
        'PORT': '13050',
        'OPTIONS': {'charset': 'WIN1252'},
    },
}

DATABASE_ROUTERS = ['utils.router.Router', ]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
    {
        'NAME': 'utils.classes'
                '.LowerCaseValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'pt-br'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

FORMAT_MODULE_PATH = [
    'fo2.formats',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    # '/var/www/static/',
]

# Necessário para o collectstatic
STATIC_ROOT = os.path.join(ROOT_DIR, "static")

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(ROOT_DIR, "media")

# Session limit
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 horas

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'fo2file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, "fo2debug.log"),
        },
    },
    'loggers': {
        'fo2': {
            'handlers': ['fo2file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'FO2L',
        'KEY_PREFIX': 'FO2K',
        'TIMEOUT': 600,
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    }
}

# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 600
# CACHE_MIDDLEWARE_KEY_PREFIX = 'FO2K'
