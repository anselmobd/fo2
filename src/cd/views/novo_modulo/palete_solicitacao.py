from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefsHpS

from cd.forms import PaleteSolicitacaoForm

from cd.queries.novo_modulo.palete_solicitacao import palete_solicitacao_query


__all__ = ['PaleteSolicitacaoView']


class PaleteSolicitacaoView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PaleteSolicitacaoView, self).__init__(*args, **kwargs)
        self.Form_class = PaleteSolicitacaoForm
        self.template_name = 'cd/novo_modulo/palete_solicitacao.html'
        self.title_name = 'Palete/Solicitacao'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        paletes = palete_solicitacao_query(
            self.cursor, solicitacao=self.solicitacao)

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
