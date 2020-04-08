from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.http import JsonResponse
from django.views import View

from estoque import classes


class Movimenta(PermissionRequiredMixin, View):

    template_name = 'estoque/ajax/movimenta.html'

    def __init__(self):
        self.permission_required = 'estoque.can_transferencia'

    def trata_input(self):
        try:
            self.data['quantidade'] = int(self.data['quantidade'])
        except Exception as e:
            raise ValueError('Quantidade deve ser numérica')

        if self.data['num_doc'] == '-':
            self.data['num_doc'] = None
        if self.data['descricao'] == '-':
            self.data['descricao'] = None
        self.data['cria_num_doc'] = \
            self.data['cria_num_doc'].upper() == 'S'

    def init_transfere(self):
        self.transf = classes.Transfere(
            self.cursor,
            self.request,
            *(self.data[f] for f in [
                'tip_mov', 'nivel', 'ref', 'tam', 'cor', 'quantidade',
                'deposito_origem', 'deposito_destino',
                'nova_ref', 'novo_tam', 'nova_cor',
                'num_doc', 'descricao', 'cria_num_doc']),
        )

    def get(self, request, **kwargs):
        self.request = request
        self.data = kwargs
        self.cursor = connections['so'].cursor()

        try:
            self.trata_input()
            self.init_transfere()
        except Exception as e:
            self.data.update({
                'result': 'ERR',
                'descricao_erro': str(e),
            })
            return JsonResponse(self.data, safe=False)

        self.data.update({
            'num_doc': self.transf.num_doc,
            'result': 'OK',
        })
        return JsonResponse(self.data, safe=False)
