from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

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

        if self.data['descricao'] == '-':
            self.data['descricao'] = None
        self.data['cria_num_doc'] = \
            self.data['cria_num_doc'].upper() in 'TS'
        self.data['executa'] = \
            self.data['executa'].upper() in 'TS'

        self.data.update({
            'status': 'inicializado',
        })

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

        self.data.update({
            'status': 'analisado',
        })

    def exec_transfere(self):
        if self.data['executa']:
            self.transf.exec()

            self.data.update({
                'status': 'executado',
            })

    def get(self, request, **kwargs):
        self.request = request
        self.data = kwargs
        self.cursor = db_cursor_so(request)

        self.data.update({
            'status': 'requisitado',
        })

        try:
            self.trata_input()
            self.init_transfere()
            self.exec_transfere()
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
