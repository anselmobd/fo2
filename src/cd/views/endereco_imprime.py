from pprint import pprint

# from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import query_endereco


class EnderecoImprime(O2BaseGetPostView):  # PermissionRequiredMixin, 

    def __init__(self, *args, **kwargs):
        super(EnderecoImprime, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoImprimeForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        # self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco_imprime.html'
        self.title_name = 'Imprime Endereços'
        self.cleaned_data2self = True

        self.impresso = 'etiqueta-de-endereco'

    def verifica_impresso(self):
        try:
            self.obj_impresso = lotes.models.Impresso.objects.get(
                slug=self.impresso)
            self.context.update({
                'cod_impresso': self.obj_impresso.nome,
            })
            return True
        except lotes.models.Impresso.DoesNotExist:
            self.context.update({
                'mensagem': f"Impresso '{self.impresso}' não cadastrado",
            })
            return False


    def verifica_usuario_impresso(self):
        try:
            self.usuario_impresso = lotes.models.UsuarioImpresso.objects.get(
                usuario=self.request.user, impresso=self.obj_impresso)
            self.context.update({
                'modelo': self.usuario_impresso.modelo.codigo,
            })
            return True
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'mensagem': f"Impresso '{self.impresso}' não cadastrado para o usuário",
            })
            return False

    def print(self):
        if not (
            self.verifica_impresso()
            and self.verifica_usuario_impresso()
        ):
            return False

        teg = TermalPrint(
            self.usuario_impresso.impressora_termica.nome,
            file_dir=f"impresso/{self.impresso}/%Y/%m"
        )
        teg.template(self.usuario_impresso.modelo.gabarito, '\r\n')
        teg.printer_start()
        try:
            imprime = False
            for row in self.data:
                if row['end'] == self.inicial:
                    imprime = True
                if imprime:
                    teg.context(row)
                    teg.printer_send()
                    if row['end'] == self.final:
                        break
        finally:
            teg.printer_end()

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        # self.final = self.final.upper()
        self.final = self.inicial.upper()

        self.data = query_endereco(cursor, 'TO')

        if not next(
            (
                row for row in self.data
                if row["end"] == self.inicial
            ),
            False
        ):
            self.context.update({
                # 'mensagem': 'Endereço inicial não existe',
                'mensagem': 'Endereço não existe',
            })
            return

        # if not next(
        #     (
        #         row for row in self.data
        #         if row["end"] == self.final
        #     ),
        #     False
        # ):
        #     self.context.update({
        #         'mensagem': 'Endereço final não existe',
        #     })
        #     return

        if self.print():
            self.context.update({
                'mensagem': 'OK!',
            })
