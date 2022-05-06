from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import Perf

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


class NovoEstoque(O2BaseGetPostView):

    def __init__(self):
        super(NovoEstoque, self).__init__()
        self.Form_class = cd.forms.NovoEstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'
