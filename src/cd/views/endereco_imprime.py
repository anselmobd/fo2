from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from cd.forms.endereco import EnderecoImprimeForm
from cd.functions.estante import gera_estantes_enderecos
from cd.queries.endereco import (
    add_endereco,
    query_endereco,
)


class EnderecoImprime(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EnderecoImprime, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoImprimeForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco_imprime.html'
        self.title_name = 'Imprime Endereços'
        self.cleaned_data2self = True

    def mount_context(self):
        dados = query_endereco('TO')
        pprint(dados[:2])
