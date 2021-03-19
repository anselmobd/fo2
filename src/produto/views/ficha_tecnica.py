from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import produto.forms
import produto.queries


class FichaTecnica(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FichaTecnica, self).__init__(*args, **kwargs)
        self.Form_class = produto.forms.ReferenciaNoneForm
        self.template_name = 'produto/ficha_tecnica.html'
        self.title_name = 'Ficha técnica'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']

        if ref != '':
        cursor = db_cursor_so(self.request)

        data = produto.queries.ref_inform(cursor, ref)
        if len(data) == 0:
            self.context.update({
                'erro': 'Referência não encontrada',
            })
