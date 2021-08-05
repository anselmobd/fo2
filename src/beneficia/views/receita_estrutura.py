from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import beneficia.forms
import beneficia.queries


class ReceitaEstrutura(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ReceitaEstrutura, self).__init__(*args, **kwargs)
        self.Form_class = beneficia.forms.ReceitaForm
        self.template_name = 'beneficia/receita_estrutura.html'
        self.title_name = 'Receita'
        self.get_args = ['receita']
        self.cleaned_data2self = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
