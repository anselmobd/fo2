from pprint import pprint
from datetime import timedelta

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

import cd.forms
from cd.queries.novo_modulo import atividade_cd63


class AtividadeCD63(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(AtividadeCD63, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.AtividadeCD63Form
        self.template_name = 'cd/novo_modulo/atividade_cd63.html'
        self.title_name = 'Atividade no CD'

        self.table_defs = TableDefs(
            {
                'data': ['Data'],
                'usuario': ['Obs.'],
                'dep': ['Depósito'],
                'atividade': ['Atividade'],
                'qtd': ['Quantidade'],
            },
            ['header'],
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data_de = self.form.cleaned_data['data_de']
        data_ate = self.form.cleaned_data['data_ate']
        if not data_ate:
            data_ate = data_de
        data_ate = data_ate + timedelta(days=1)
        self.context['data_de'] = data_de
        self.context['data_ate'] = data_ate

        data = atividade_cd63.query(cursor, data_de, data_ate)
        if not data:
            self.context['erro'] = 'Atividade não encontrada'
            return

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
        })
