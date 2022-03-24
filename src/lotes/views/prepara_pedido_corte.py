from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries
from lotes.queries.pedido.ped_alter import altera_pedido
from lotes.queries.pedido.mensagem_nf import cria_mens_nf
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
            return ('ERRO', "Pedido não encontrado!")

        dados, clientes = romaneio_corte.query_completa(cursor, data, nf=True, cliente_slug=cliente)
        pprint(dados)
        pprint(clientes)

        # MPCFM - Movimentação de Peças Cortadas da Filial p/ Matriz; Data: 2022-03-16
        # Produção para o cliente Renner. Pedido(5214524)-OP(34023), Pedido(5214547)-OP(34027)
        # Produção para estoque. OP(34082, 34307, 34339, 34262, 34297)

        if cliente == 'estoque':
            observacao = (
                "[MPCFM] Movimentacao de Pecas Cortadas da Filial para Matriz; Data: 2022-03-16",
                f"Producao para estoque. {dados[0]['obs']}",
            )
        else:
            observacao = (
                "[MPCFM] Movimentacao de Pecas Cortadas da Filial para Matriz; Data: 2022-03-16",
                f"Producao para o cliente {cliente.capitalize()}. {dados[0]['obs']}",
            )

        cria_mens_nf(cursor, pedido, observacao)
        altera_pedido(cursor, pedido, 3, "\n".join(observacao))

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

