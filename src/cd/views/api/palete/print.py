from pprint import pprint

from django.http import JsonResponse
from django.views import View

from cd.classes.palete import Plt


class PaletePrint(View):

    def palete_print_mount(self, code):
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


    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        data = self.palete_print_mount(code)
        return JsonResponse(data, safe=False)
