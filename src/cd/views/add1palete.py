from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from cd.forms.add1palete import Add1PaleteForm
from cd.queries.palete import custom_add_palete


class Add1Palete(O2BaseGetPostView, PermissionRequiredMixin):

    def __init__(self, *args, **kwargs):
        super(Add1Palete, self).__init__(*args, **kwargs)
        self.permission_required = 'cd.can_admin_pallet'
        self.Form_class = Add1PaleteForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.template_name = 'cd/add1palete.html'
        self.title_name = 'Adiciona Palete'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        status, inseridos = custom_add_palete(cursor, prefix=self.tipo)

        if status == "OK":
            self.context['msg'] = f"Inserido palete {inseridos[0]}"
        else:
            self.context['msg'] = f"Erro <{status}>, inserindo palete {inseridos[0]}"
