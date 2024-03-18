from pprint import pprint

from django.http import JsonResponse
from django.views import View


class ProduzLote(View):

    def process(self, request, kwargs):
        return ('OK', "OK!")

    def response(self, result):
        status, message = result
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        result = self.process(request, kwargs)
        return JsonResponse(self.response(result), safe=False)
