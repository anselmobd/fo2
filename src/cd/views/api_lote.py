from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from cd.queries.lote import tira_lote


def retira_lote(request, lote):
    data = {}
    cursor = db_cursor_so(request)
    err_message = tira_lote(cursor, lote)
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
