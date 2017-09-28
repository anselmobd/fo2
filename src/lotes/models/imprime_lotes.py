from fo2.models import rows_to_dict_list

from lotes.models.base import *


def get_imprime_lotes(cursor, op, tam, cor, order, oc_ini, oc_fim,
                      pula, qtd_lotes):
    # get dados de lotes
    return get_lotes(cursor, op=op, tam=tam, cor=cor, order=order,
                     oc_ini=oc_ini, oc_fim=oc_fim,
                     pula=pula, qtd_lotes=qtd_lotes)
