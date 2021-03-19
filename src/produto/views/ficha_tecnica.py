from pprint import pprint

from base.views import O2BaseGetPostView

import produto.forms


class FichaTecnica(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FichaTecnica, self).__init__(*args, **kwargs)
        self.Form_class = produto.forms.ReferenciaForm
        self.template_name = 'comercial/ficha_tecnica.html'
        self.title_name = 'Ficha técnica'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']

        if ref == '':
            return
