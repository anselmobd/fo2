from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from cd.classes.palete import Plt
from cd.queries.palete import add_palete


def palete_add(request):
    data = {}
    cursor = db_cursor_so(request)
    result, message = add_palete(cursor)
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


def palete_print_mount(code):
    try:
        code_ok = Plt(code).verify()
    except ValueError:
        code_ok = False
    if not code_ok:
        return {
            'result': 'ERRO',
            'state': 'Código inválido',
        }

    return {
        'result': 'OK',
        'code': code,
    }


def palete_print(request, code):
    data = palete_print_mount(code)
    return JsonResponse(data, safe=False)
