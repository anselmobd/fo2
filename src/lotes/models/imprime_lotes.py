from fo2.models import rows_to_dict_list

from lotes.models.base import *


def get_imprime_lotes(cursor, op, oc_ini, oc_fim, order='oc'):
    # get dados de lotes
    return get_lotes(cursor, op=op, oc_ini=oc_ini, oc_fim=oc_fim, order=order)
