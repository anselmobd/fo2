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

from lotes.models.op import OpCortada


class MarcaOpCortada(View):

    def process(self, request, kwargs):
        cursor = db_cursor_so(request)

        op = kwargs['op']

        try:
            op_object = OpCortada.objects.get(op=op)
        except OpCortada.DoesNotExist:
            op_object = None

        try:
            if op_object:
                op_object.detete()
                return 'DESMARCADA'
            else:
                op_object = OpCortada(op=op)
                op_object.save()
                return 'MARCADA'
        except Exception:
            return 'ERRO'

    def response(self, result):
        status, message = result
        return {
            'status': status,
        }

    def get(self, request, *args, **kwargs):
        result = self.process(request, kwargs)
        return JsonResponse(self.response(result), safe=False)
