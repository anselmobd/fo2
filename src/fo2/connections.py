from pprint import pprint

from django.db import connections


def db_conn(name):
    return connections[name]
