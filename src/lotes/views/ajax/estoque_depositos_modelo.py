from pprint import pprint

from django.db import connections
from django.http import JsonResponse

from systextil.queries.deposito.total_modelo import total_modelo_deposito


def estoque_depositos_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        total_est = total_modelo_deposito(
            cursor, modelo, ('101', '102', '103', '122', '231')
        )
    except Exception as e:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar estoque nos depósitos',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_est': total_est,
    })
    return JsonResponse(data, safe=False)
