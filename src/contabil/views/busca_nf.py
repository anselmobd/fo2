from pprint import pprint

from base.views import O2BaseGetPostView

import contabil.forms as forms


class BuscaNF(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(BuscaNF, self).__init__(*args, **kwargs)
        self.Form_class = forms.buscaNFForm
        self.template_name = 'contabil/busca_nf.html'
        self.title_name = 'Busca nota fiscal'

    def mount_context(self):
        pass
