from pprint import pprint

from django.db import connections
from django.db.models import Exists, OuterRef
from django.http import JsonResponse

from systextil.queries.deposito.total_modelo import totais_modelos_depositos

import comercial.models


def estoque_depositos_modelo(request, modelo, filtra=''):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        if filtra == 'm':
            metas = comercial.models.MetaEstoque.objects
            metas = metas.annotate(antiga=Exists(
                comercial.models.MetaEstoque.objects.filter(
                    modelo=OuterRef('modelo'),
                    data__gt=OuterRef('data')
                )
            ))
            metas = metas.filter(antiga=False)
            metas = metas.exclude(venda_mensal=0)
            metas = metas.values('modelo')
            modelos = tuple(m['modelo'] for m in metas)
        else:
            modelos = None
        pprint(modelos)
        totais = totais_modelos_depositos(
            cursor, ('101', '102', '103', '122', '231'), modelos)
        try:
            total_est = totais[modelo]
        except KeyError:
            total_est = 0
        data.update({
            'result': 'OK',
            'total_est': total_est,
        })

    except Exception as e:
        raise e
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar estoque nos depósitos',
        })

    return JsonResponse(data, safe=False)
