from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.queries.lote import op_de_lote

import cd.forms
from cd.queries.novo_modulo import cd_lote_hist


class AtividadeCD63(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(AtividadeCD63, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.AtividadeCD63Form
        self.template_name = 'cd/novo_modulo/atividade_cd63.html'
        self.title_name = 'Atividade no CD'

        self.table_defs = TableDefs(
            {
                'atividade': ['Atividade'],
                'cod_container': ['Palete'],
                # 'endereco': ['Endereço'],  # não utilizado em movimentos de lotes
                'data_hora': ['Quando'],
                'sistema': ['Sistema'],
                'tela': ['Tela'],
                'login': ['Usuário'],
                'usuario': ['Obs.'],
            },
            ['header'],
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        lote = self.form.cleaned_data['lote']
        self.context['lote'] = lote

        data = op_de_lote.query(cursor, lote)
        if not data:
            self.context['erro'] = 'Lote não encontrado'
            return

        self.context['op'] = f"{data[0]['op']}"

        data = cd_lote_hist.query(cursor, lote)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
        })
