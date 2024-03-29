from pprint import pprint

from django.conf import settings
from django.db import connections

from geral.functions import is_alternativa
from utils.functions.oracle import get_oracle_conn


fo2_db_so = settings.FO2_DEFAULT_SYSTEXTIL_DB
fo2_db_sn = settings.FO2_ALTER_SYSTEXTIL_DB


def db_conn(name, request=None):
    if request and name == fo2_db_so:
        # 2021-02-22 url alternativa aponta db alernativo
        if is_alternativa(request):
            return connections[fo2_db_sn]
        else:
            return connections[fo2_db_so]
            # return get_oracle_conn(**settings.DATABASES_EXTRAS['sn'])
    return connections[name]


def db_conn_so(request=None):
    return db_conn(fo2_db_so, request)


def db_cursor(name, request=None):
    return db_conn(name, request).cursor()


def db_cursor_so(request=None):
    return db_conn_so(request).cursor()
