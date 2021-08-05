from pprint import pprint

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
        self.cursor = db_cursor_so(self.request)

        dados = beneficia.queries.receita_inform(self.cursor, self.receita)

        self.context.update({
            'headers': ['Receita', 'Descrição'],
            'fields': ['ref', 'descr'],
            'dados': dados,
        })
