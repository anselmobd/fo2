from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from utils.views import totalize_data

import lotes.queries.op


def op_producao_modelo(request, modelo):
    cursor = db_cursor_so(request)
    data = {
        'modelo': modelo,
    }

    try:
        data_op = lotes.queries.op.busca_op(
            cursor, modelo=modelo, tipo='v', tipo_alt='p',
            situacao='a', posicao='p', cached=True)

        if len(data_op) == 0:
            total_op = 0
        else:
            totalize_data(data_op, {
                'sum': ['QTD_AP'],
                'descr': {'OP': 'T:'},
            })
            total_op = data_op[-1]['QTD_AP']

    except Exception as e:
        raise e
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar OP',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_op': total_op,
    })
    return JsonResponse(data, safe=False)
