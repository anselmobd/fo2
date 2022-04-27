from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import comercial.forms


class NfEspecial(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(NfEspecial, self).__init__()
        self.permission_required = 'comercial.can_gerenciar_nf_especial'
        self.Form_class = comercial.forms.NfEspecialForm
        self.cleaned_data2self = True
        self.template_name = 'comercial/gerencia/nf_especial.html'
        self.title_name = 'NF especial'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
