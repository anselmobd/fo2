from pprint import pprint

from django.db import connections

from geral.functions import is_alternativa


def db_conn(name, request=None):
    if request and name == 'so':
        # 2021-02-22 alternativa aponta para núvem e não alernativa para local
        if is_alternativa(request):
            return connections['sn']
        else:
            return connections['so']
    return connections[name]
