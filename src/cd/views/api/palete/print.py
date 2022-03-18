from pprint import pprint

from django.http import JsonResponse

from cd.classes.palete import Plt


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
