from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from estoque.classes import Transfere
from estoque.queries.posicao_estoque import posicao_estoque

__all__ = ['ZeraRef']


class ZeraRef(PermissionRequiredMixin, View):
    
    def __init__(self):
        self.permission_required = 'estoque.pode_zerar_depositos'

    def get(self, request, **kwargs):
        context = kwargs
        cursor = db_cursor_so(request)

        tam_cor_qtd = posicao_estoque(
            cursor, 1, context['ref'], '', '',
            context['dep'], zerados=False, group='tc'
        )

        num_doc = '0'
        descricao = f"Zera ref. {context['ref']} no dep. {context['dep']}"
        cria_num_doc = 's'

        for row in tam_cor_qtd:
            if row['qtd'] > 0:
                tip_mov = 'sai-bal'
                quantidade = row['qtd']
                deposito_origem = context['dep']
                deposito_destino = None
            else:
                tip_mov = 'ent-bal'
                quantidade = -row['qtd']
                deposito_origem = None
                deposito_destino = context['dep']

            try:
                transf = Transfere(
                    cursor,
                    request,
                    tip_mov,
                    '1',
                    context['ref'],
                    row['tam'],
                    row['cor'],
                    quantidade,
                    deposito_origem,
                    deposito_destino,
                    '',  # nova_ref
                    '',  # novo_tam
                    '',  # nova_cor
                    num_doc,
                    descricao,
                    cria_num_doc,
                )
                transf.exec()
                num_doc = transf.num_doc
                descricao = ''
                cria_num_doc = 'n'
                row.update({'result': 'OK'})
            except Exception as e:
                row.update({
                    'result': 'ERRO',
                    'message': str(e),
                })

        context['tam_cor_qtd'] = [
            {
                k: v 
                for k, v in d.items()
                if k in ['tam', 'cor', 'qtd', 'result', 'message']
            }
            for d in tam_cor_qtd
        ]      

        return JsonResponse(context, safe=False)
