import re
from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries
from lotes.queries.pedido.ped_alter import (
    altera_pedido,
    altera_pedido_itens,
)
from lotes.queries.pedido.mensagem_nf import cria_mens_nf
from lotes.queries.producao.romaneio_corte import producao_ops_finalizadas
from lotes.views.prepara_pedido_compra_matriz import cria_pedido_compra_matriz


class PreparaPedidoCorte(View):

    def process(self, request, kwargs):
        cursor = db_cursor_so(request)

        data = kwargs['data']
        cliente = kwargs['cliente']
        pedido = kwargs['pedido']

        dados = lotes.queries.pedido.ped_inform(cursor, pedido, empresa=3)
        if not dados:
            return ('ERRO', "Pedido não encontrado!")
        if dados[0]['COD_CANCELAMENTO'] != 0:
            return ('ERRO', "Pedido cancelado!")
        if dados[0]['NF'] is not None:
            return ('ERRO', "Pedido faturado!")
        if dados[0]['OBSERVACAO']:
            if re.search('^\[MPCFM\] ', dados[0]['OBSERVACAO']):
                return ('ERRO', "Pedido já preparado!")

        dados, clientes = producao_ops_finalizadas.query(
            cursor, data, para_nf=True, cliente_slug=cliente)

        #   exemplos de observações:
        # MPCFM - Movimentação de Peças Cortadas da Filial p/ Matriz; Data: 2022-03-16
        # Produção para o cliente Renner. Pedido(5214524)-OP(34023), Pedido(5214547)-OP(34027)
        #   ou
        # MPCFM - Movimentação de Peças Cortadas da Filial p/ Matriz; Data: 2022-03-16
        # Produção para estoque. OP(34082, 34307, 34339, 34262, 34297)

        if cliente == 'estoque':
            observacao = (
                f"[MPCFM] Movimentacao de Pecas Cortadas da Filial para Matriz; Data: {data}",
                f"Producao para estoque: {clientes[cliente]['obs']}",
            )
        else:
            observacao = (
                f"[MPCFM] Movimentacao de Pecas Cortadas da Filial para Matriz; Data: {data}",
                f"Producao para o cliente {cliente.capitalize()}: {clientes[cliente]['obs']}",
            )

        cria_mens_nf(cursor, pedido, observacao)

        altera_pedido_itens(cursor, pedido, 302, 'RJ', dados)

        qtd_itens = 0
        for row in dados:
            qtd_itens += row['mov_qtd']
        altera_pedido(cursor, data, pedido, 3, qtd_itens, "\n".join(observacao))

        if not cria_pedido_compra_matriz(cursor, pedido):
            return ('ERRO', "Algum erro ocorreu durante a criação do pedido de compra!")

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

