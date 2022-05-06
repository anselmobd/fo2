from pprint import pprint

from base.views import O2BaseGetPostView

import cd.forms


class Estoque(O2BaseGetPostView):

    def __init__(self):
        super(Estoque, self).__init__()
        self.Form_class = cd.forms.EstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'
