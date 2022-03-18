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
    cursor = db_cursor_so(request)
    data = query_palete('N', 'A')

    last_palete = None
    ok = False
    for row in data:
        ok = mark_palete_impresso(cursor, row['palete'])
        if ok:
            last_palete = row['palete']
        else:
            break

    if ok:
        context = {
            'result': 'OK',
                'state': f"Último palete marcado: {last_palete}",
        }
    else:
        if last_palete:
            context = {
                'result': 'ERROR',
                'state': f"Último palete marcado: {last_palete}",
            }
        else:
            context = {
                'result': 'ERROR',
                'state': "Nenhum palete marcado",
            }
    return JsonResponse(context, safe=False)
