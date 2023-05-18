from pprint import pprint

from django.contrib.postgres.aggregates import StringAgg

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.dictlist import queryset2dictlist, dictlist_agg
from utils.functions.models.row_field import PrepRows
from utils.table_defs import TableDefsHpS

from lotes.functions.varias import modelo_de_ref

from produto.forms import ModeloForm
from produto import models

from cd.queries.novo_modulo.palete_solicitacao import palete_solicitacao_query


__all__ = ['PaleteSolicitacaoView']


class PaleteSolicitacaoView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PaleteSolicitacaoView, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm
        self.template_name = 'cd/novo_modulo/palete_solicitacao.html'
        self.title_name = 'Palete/Solicitacao'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        modelo = int(self.modelo)

        paletes = palete_solicitacao_query(self.cursor)

        self.context['paletes'] = TableDefsHpS({
            'palete': "Palete",
            'endereco': "Endereço",
            'qpedsol': "Qtd. solict. pedido",
            'pedsol': "Solict. pedido",
            'qagrupsol': "Qtd. solict. agrupamento",
            'agrupsol': "Solict. agrupamento",
        }).hfs_dict()
        self.context['paletes'].update({
            'data': paletes,
            'thclass': 'sticky',
            'empty': "Nenhum encontrado",
        })
        pprint(self.context)
