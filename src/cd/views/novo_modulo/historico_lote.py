from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.queries.lote import op_de_lote

import cd.forms
from cd.queries.novo_modulo import cd_lote_hist


class HistoricoLote(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(HistoricoLote, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.ALoteForm
        self.template_name = 'cd/novo_modulo/historico_lote.html'
        self.title_name = 'Histórico de lote'
        self.get_args = ['lote']

        self.table_defs = TableDefs(
            {
                'usuario': ['Usuário'],
                'data_hora': ['Quando'],
                'atividade': ['Atividade'],
                'cod_container': ['Palete'],
                'endereco': ['Endereço'],
                'ordem_producao': ['OP'],
                'ordem_confeccao': ['OC'],
            },
            ['header'],
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        lote = self.form.cleaned_data['lote']

        data = op_de_lote.query(cursor, lote)
        if not data:
            self.context['erro'] = 'Lote não encontrado'
            return

        self.context['op'] = data[0]['op']

        data = cd_lote_hist.query(cursor, lote)
        
        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
        })
