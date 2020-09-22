from pprint import pprint

from django.db import connections
from django.http import JsonResponse

import estoque.queries


def estoque_depositos_modelo(request, modelo):
    print('estoque_depositos_modelo')
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        _, _, _, _, total_est = \
            estoque.queries.grade_estoque(
                cursor, dep=('101', '102', '231'), modelo=modelo)

    except Exception:
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
