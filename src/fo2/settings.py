import os
from . import __version__, __version__date__

from .db_password import *


PROJ_VERSION = __version__
PROJ_VERSION_DATE = __version__date__

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

with open(os.path.join(ROOT_DIR, 'etc/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

DEBUG = True

DEBUG_CURSOR_EXECUTE = True
DEBUG_CURSOR_EXECUTE_PRT = True

ALLOWED_HOSTS = [
    # production
    '192.168.1.96',
    'in.cuecasduomo.com.br',
    '177.23.138.90',
    'vox.cuecasduomo.com',
    '192.141.163.26',
    'velosat.cuecasduomo.com',
    '177.11.1.188',
    'redeon.cuecasduomo.com',
    'intranet', 'intranet.tussor',
    'alterintranet', 'alterintranet.tussor',
    'intranet.tussor.com.br',
    'alterintranet.tussor.com.br',
    'intranet.cuecasduomo.com', 'intranet.cuecasduomo.com.br',
    'velosat.cuecasduomo.com.br',
    'alterintranet.cuecasduomo.com', 'alterintranet.cuecasduomo.com.br',
    'intranet.agator.com', 'intranet.agator.com.br',
    'alterintranet.agator.com', 'alterintranet.agator.com.br',
    # development
    '192.168.1.242', '192.168.1.225', '192.168.15.10',
    'localhost',
    'agator.local', 'tussor.local',
    'alteragator.local', 'altertussor.local',
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
    # 'nested_inline',
    # Project
    'base',
    'beneficia',
    'cd',
    'comercial',
    'contabil',
    'email_signature',
    'estoque',
    'geral',
    'insumo',
    'itat',
    'logistica',
    'lotes',
    'manutencao',
    'o2',
    'persona',
    'produto',
    'remote_files',
    'servico',
    'systextil',
    'tussor',
    'utils',
]

MIDDLEWARE = [
    'fo2.virtualhostmiddleware.VirtualHostMiddleware',
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
    'utils.middlewares.AlterRouterMiddleware',
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
    '^/meuip/$',
    '^/encerrar_intranet/$',
    '^/static/.*$',
]
N2LOL_ALLOWED_IP_BLOCKS = [r'^192\.168\.1\..+$', r'^127\.0\.0\.1$']

ROOT_URLCONF = 'fo2.urls_tussor'

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
                'utils.pages_context.alter_context_processor',
                'geral.functions.get_list_geral_paineis',
                'email_signature.context.processor',
                'estoque.pages_context.get_estoque_movimentos',
                'base.pages_context.main',
            ],
        },
    },
]

SETTINGS_EXPORT = [
    'PROJ_VERSION',
    'PROJ_VERSION_DATE',
]

WSGI_APPLICATION = 'fo2.wsgi.application'


DATABASES = {
    'default': {  # intranet
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "tussor_dev_fo2_production",
        'USER': "tussor_dev_fo2",
        'PASSWORD': "1C94B9CE0FD2B81DF12E923E3E5FF9217CA12A6A8CF1F9C9989C43ED034A9F8D",
        'HOST': 'localhost',
        'PORT': '5434',
    },
    'systextil_log': {  # intranet - logs do systextil
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "tussor_dev_fo2_production",
        'USER': "tussor_dev_fo2",
        'PASSWORD': "1C94B9CE0FD2B81DF12E923E3E5FF9217CA12A6A8CF1F9C9989C43ED034A9F8D",
        'HOST': 'localhost',
        'PORT': '5434',
    },
    'sn': {  # systextil
        'ENGINE': 'django.db.backends.oracle',
        # 'NAME': 'localhost:14521/db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        'NAME': '152.67.55.216:1521/db_pdb1.sub02011943440.tussorvcn.oraclevcn.com',
        'USER': 'systextil',
        'PASSWORD': DBPASS_SH,
    },
    'persona': {  # Nasajon
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nasajon_db",
        'USER': "postgres",
        'PASSWORD': DBPASS_PERSONA,
        'HOST': 'localhost',
        'PORT': '25433',
    },
}

FO2_DEFAULT_SYSTEXTIL_DB = os.getenv('DEFAULT_SYSTEXTIL_DB', 'so')
_FO2_ALTER_SYSTEXTIL_DICT = {
    'so': 'sn',
    'sn': 'so',
}
FO2_ALTER_SYSTEXTIL_DB = _FO2_ALTER_SYSTEXTIL_DICT[FO2_DEFAULT_SYSTEXTIL_DB]

DATABASES_EXTRAS = {
    'f1': {  # F1 e SCC
        'ENGINE': 'firebird',
        'NAME': '/dados/db/f1/f1.cdb',
        'USER': 'sysdba',
        'PASSWORD': DBPASS_F1,
        'HOST': 'localhost',
        'PORT': 23050,
        'OPTIONS': {'charset': 'WIN1252'},
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'AUTOCOMMIT': None,
        'DIALECT': 3,
    },
}

DATABASE_ROUTERS = ['utils.router.Router', ]

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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = False

USE_THOUSAND_SEPARATOR = True

FORMAT_MODULE_PATH = [
    'fo2.formats',
]

LOCAL_LOCALE = ('pt_BR', 'UTF-8')

# Static files (CSS, JavaScript, Images)
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
SESSION_COOKIE_AGE = 10 * 60 * 60  # 10 horas

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

INTERNAL_IPS = (
    '127.0.0.1',
)

MIKROTIK = {
    'user': 'anselmo',
    'key_file': '/home/anselmo/.ssh/id_rsa',
}

FILE_UPLOAD_PERMISSIONS = 0o644

# Fase 1:
# . Desligada rotina de passar quantidades para conserto
# . Só pode imprimir etiquetas parciais, se for de solicitações
#   criadas antes de 2022-02-01 18h00
# . Tira do conserto todos os lotes que não pertencem a solicitações
#   criadas antes de 2022-02-01 18h00
DESLIGANDO_CD_FASE = 1

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
