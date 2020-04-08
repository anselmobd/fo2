from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.http import JsonResponse
from django.views import View


class Movimenta(PermissionRequiredMixin, View):

    template_name = 'estoque/ajax/movimenta.html'

    def __init__(self):
        self.permission_required = 'estoque.can_transferencia'

    def get(self, request, tipo, *args, **kwargs):
        cursor = connections['so'].cursor()
        data = {
            'tipo': tipo,
        }

        erro = False
        state = 'teste'

        if erro:
            data.update({
                'result': 'ERR',
                'descricao_erro': 'Erro ao alterar direito',
            })
            return JsonResponse(data, safe=False)

        data.update({
            'result': 'OK',
            'state': state,
        })
        return JsonResponse(data, safe=False)
