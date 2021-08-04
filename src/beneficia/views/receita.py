from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import beneficia.forms


class Receita(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Receita, self).__init__(*args, **kwargs)
        self.Form_class = beneficia.forms.ReferenciaForm
        self.template_name = 'beneficia/receita.html'
        self.title_name = 'Receita'
        self.get_args = ['receita']

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
