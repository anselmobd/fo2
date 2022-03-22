from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries
from lotes.queries.pedido.ped_alter import altera_pedido
from lotes.queries.producao import romaneio_corte


class PreparaPedidoCorte(View):

    def process(self, request, kwargs):
        cursor = db_cursor_so(request)

        data = kwargs['data']
        cliente = kwargs['cliente']
        pedido = kwargs['pedido']

        dados = lotes.queries.pedido.ped_inform(cursor, pedido, empresa=3)
        pprint(dados)
        if not dados:
            self.result = ('ERRO', "Pedido não encontrado!")
            return

        dados, clientes = romaneio_corte.query_completa(cursor, data, nf=True, cliente_slug=cliente)
        pprint(dados)
        pprint(clientes)

        observacao = dados[0]['obs']
        altera_pedido(cursor, pedido, 3, observacao)

        self.result = ('OK', "OK!")

    def response(self):
        status, message = self.result
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        self.process(request, kwargs)
        return JsonResponse(self.response(), safe=False)

