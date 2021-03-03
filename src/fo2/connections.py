from pprint import pprint

from django.conf import settings
from django.db import connections

from geral.functions import is_alternativa


def db_conn(name, request=None):
    so = settings.FO2_DEFAULT_SYSTEXTIL_DB
    sn = settings.FO2_ALTER_SYSTEXTIL_DB
    if request and name == so:
        # 2021-02-22 url alternativa aponta db alernativo
        if is_alternativa(request):
            return connections[sn]
        else:
            return connections[so]
    return connections[name]
