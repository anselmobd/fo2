from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import beneficia.forms
import beneficia.queries


class Receita(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Receita, self).__init__(*args, **kwargs)
        self.Form_class = beneficia.forms.ReceitaForm
        self.template_name = 'beneficia/receita.html'
        self.title_name = 'Receita'
        self.get_args = ['receita']
        self.cleaned_data2self = True

    def mount_context(self):
        if not self.receita:
            return
        self.context.update({'render': True})

        self.cursor = db_cursor_so(self.request)

        dados = beneficia.queries.receita_inform(self.cursor, self.receita)

        if not dados:
            return

        self.context.update({
            'headers': ['Receita', 'Descrição'],
            'fields': ['ref', 'descr'],
            'dados': dados,
        })

        sg_dados = beneficia.queries.receita_subgrupo(self.cursor, self.receita)

        self.context.update({
            'sg_headers': ['Subgrupo', 'Descrição'],
            'sg_fields': ['subgrupo', 'descr'],
            'sg_dados': sg_dados,
        })

        so_dados = beneficia.queries.receita_cores(self.cursor, self.receita)

        for row in so_dados:
            row['cor|LINK'] = reverse(
                'beneficia:receita_estrutura',
                args=[
                    '.'.join([
                        '5',
                        self.receita,
                        row['subgrupo'],
                        row['cor'],
                    ])
                ],
            )

        self.context.update({
            'so_headers': ['Subgrupo', 'Cor', 'Descrição'],
            'so_fields': ['subgrupo', 'cor', 'descr'],
            'so_dados': so_dados,
        })
