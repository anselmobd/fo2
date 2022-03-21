from multiprocessing import context
from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from cd.queries.palete import add_palete, query_palete, mark_palete_printed


def palete_add(request, quant):
    data = {}
    cursor = db_cursor_so(request)
    err_message = add_palete(cursor, quant)
    if err_message:
        data.update({
            'result': 'ERROR',
            'state': err_message,
        })
    else:
        data.update({
            'result': 'OK',
            'state': 'OK!',
        })
    return JsonResponse(data, safe=False)


def palete_printed(request):

    def result(status, message):
        return JsonResponse({
            'status': status,
            'message': message,
        }, safe=False)

    cursor = db_cursor_so(request)
    data = query_palete('N', 'A')

    if not data:
        return result(
            'VAZIO',
            "Todos os paletes marcados como impressos",
        )

    for row in data:
        err_message = mark_palete_printed(cursor, row['palete'])
        if err_message:
            return result(
                'ERRO',
                f"Erro ao marcar palete {row['palete']}. {err_message}",
            )

    return result(
        'OK',
        f"OK! Último palete marcado: {row['palete']}",
    )
