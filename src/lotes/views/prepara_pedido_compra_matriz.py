import re
from pprint import pprint

from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries
from lotes.queries.pedido.ped_alter import (
    exclui_pedido_compra_matriz_capa,
    inclui_pedido_compra_matriz_capa,
    emite_pedido_compra_matriz,
    inclui_pedido_compra_matriz_itens,
    exclui_pedido_compra_matriz_itens,
    get_pedido_compra_matriz_itens,
    pedido_matriz_de_pedido_filial,
)


def cria_pedido_compra_matriz(cursor, pedido_filial):
    pedido_compra = None
    try:
        pedido_compra_matriz = pedido_matriz_de_pedido_filial(cursor, pedido_filial)
        if pedido_compra_matriz:
            pedido_compra = pedido_compra_matriz[0]['pedido_compra']

            referencias =  get_pedido_compra_matriz_itens(cursor, pedido_compra)
            if len(referencias) == 0:
                exclui_pedido_compra_matriz_capa(cursor, pedido_compra)

        if not pedido_compra_matriz:
            inclui_pedido_compra_matriz_capa(cursor, pedido_filial)

        pedido_compra_matriz = pedido_matriz_de_pedido_filial(cursor, pedido_filial)

        if pedido_compra_matriz:
            pedido_compra = pedido_compra_matriz[0]['pedido_compra']

            inclui_pedido_compra_matriz_itens(cursor, pedido_filial, pedido_compra)

            emite_pedido_compra_matriz(cursor, pedido_compra)

        return pedido_compra

    except Exception:
        if pedido_compra:
            try:
                emite_pedido_compra_matriz(cursor, pedido_compra, False)
            except Exception:
                pass

            try:
                exclui_pedido_compra_matriz_itens(cursor, pedido_compra)
            except Exception:
                pass

            try:
                exclui_pedido_compra_matriz_capa(cursor, pedido_compra)
            except Exception:
                pass

        return None


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

        if cria_pedido_compra_matriz(
                cursor, pedido_filial):
            return ('OK', "OK!")
        else:
            return ('ERRO', "Algum erro ocorreu durante a criação do pedido de compra!")

    def response(self, result):
        status, message = result
        return {
            'status': status,
            'message': message,
        }

    def get(self, request, *args, **kwargs):
        result = self.process(request, kwargs)
        return JsonResponse(self.response(result), safe=False)
