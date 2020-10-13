from pprint import pprint

from django.db import connections
from django.http import JsonResponse


def libera_coleta_de_solicitacao(request, id):
    id = id[:-2]

    data = {
        'id': id,
    }
    erro = False

    cursor = connections['so'].cursor()

    if erro:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao alterar liberação de coleta',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'state': 'state',
    })
    return JsonResponse(data, safe=False)
