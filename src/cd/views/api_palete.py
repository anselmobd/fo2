from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from cd.queries.palete import add_palete


def palete_add(request):
    data = {}
    cursor = db_cursor_so(request)
    result, message = add_palete(cursor)
    if result:
        data.update({
            'result': 'OK',
        })
    else:
        data.update({
            'result': 'ERROR',
            'state': message,
        })
    return JsonResponse(data, safe=False)
