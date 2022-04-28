import re
from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries
from lotes.queries.pedido.ped_alter import (
    inclui_pedido_compra_matriz_capa,
)


class PreparaPedidoCompraMatriz(View):

    def process(self, request, kwargs):
        cursor = db_cursor_so(request)

        pedido_filial = kwargs['pedido_filial']

        dados = lotes.queries.pedido.ped_inform(cursor, pedido_filial, empresa=3)
        if not dados:
            return ('ERRO', "Pedido não encontrado!")
        if dados[0]['COD_CANCELAMENTO'] != 0:
            return ('ERRO', "Pedido cancelado!")
        if (
            (not dados[0]['OBSERVACAO'])
            or (not re.search('^\[MPCFM\] ', dados[0]['OBSERVACAO']))
        ):
            return ('ERRO', "Não é pedido preparado para faturar filial!")

        inclui_pedido_compra_matriz_capa(cursor, pedido_filial)
        # pedido_compra_matriz = get_pedido_compra_matriz(cursor, pedido_filial)
        # inclui_pedido_compra_matriz_itens(cursor, pedido_filial, pedido_compra_matriz)

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

