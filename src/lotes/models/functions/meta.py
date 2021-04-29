from pprint import pprint

import comercial.models
from lotes.views.parametros_functions import calculaMetaGiroMetas


def calculaMetaGiroTodas(cursor):
    metas = comercial.models.getMetaEstoqueAtual()
    if len(metas) == 0:
        return 0
    else:
        metas_list = calculaMetaGiroMetas(cursor, metas)
        return len(metas_list)
