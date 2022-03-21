from multiprocessing import context
from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from cd.queries.palete import add_palete, query_palete, mark_palete_impresso


def palete_add(request, quant):
    data = {}
    cursor = db_cursor_so(request)
    result, message = add_palete(cursor, quant)
    if result:
        data.update({
            'result': 'OK',
            'state': 'OK!',
        })
    else:
        data.update({
            'result': 'ERROR',
            'state': message,
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

    last_palete = None
    for row in data:
        if mark_palete_impresso(cursor, row['palete']):
            last_palete = row['palete']
        else:
            return result(
                'ERRO',
                f"Erro! Último palete marcado: {last_palete}"
                if last_palete
                else "Erro! Nenhum palete marcado!",
            )

    return result(
        'OK',
        f"OK! Último palete marcado: {last_palete}",
    )
