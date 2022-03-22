from pprint import pprint

from django.http import JsonResponse
from django.views import View


class PreparaPedidoCorte(View):

    def result(self, status, message):
        return JsonResponse({
            'status': status,
            'message': message,
        }, safe=False)

    def get(self, request, *args, **kwargs):
        return self.result(
            'OK',
            "OK!",
        )

