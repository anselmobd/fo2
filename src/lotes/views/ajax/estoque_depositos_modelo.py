from pprint import pprint

from django.db import connections
from django.http import JsonResponse

from systextil.queries.deposito.total_modelo import totais_modelos_depositos


def estoque_depositos_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        totais = totais_modelos_depositos(
            cursor, ('101', '102', '103', '122', '231'))
        try:
            total_est = totais[modelo]
        except KeyError:
            total_est = 0
        data.update({
            'result': 'OK',
            'total_est': total_est,
        })

    except Exception as e:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar estoque nos depósitos',
        })

    return JsonResponse(data, safe=False)
