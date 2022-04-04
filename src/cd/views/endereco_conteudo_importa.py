from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import query_endereco


class EnderecoImporta(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EnderecoImporta, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoImprimeForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco_conteudo_importa.html'
        self.title_name = 'Importa conteudo de endereços'
        self.cleaned_data2self = True

    def importa(self):
        self.context.update({
            'mensagem': 'problema',
        })
        return False

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        self.final = self.final.upper()

        self.data = query_endereco(cursor, 'TO')

        if not next(
            (
                row for row in self.data
                if row["end"] == self.inicial
            ),
            False
        ):
            self.context.update({
                'mensagem': 'Endereço inicial não existe',
            })
            return

        if not next(
            (
                row for row in self.data
                if row["end"] == self.final
            ),
            False
        ):
            self.context.update({
                'mensagem': 'Endereço final não existe',
            })
            return

        if self.importa():
            self.context.update({
                'mensagem': 'OK!',
            })
