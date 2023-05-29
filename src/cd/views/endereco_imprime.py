from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import query_endereco


class PrintLabel():
    
    def __init__(self, impresso, user):
        self.impresso = impresso
        self.user = user
        self.context = {}

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
        if self.user.is_anonymous:
            self.context.update({
                'mensagem': f"Usuário não identificado",
            })
            return False
        try:
            self.usuario_impresso = lotes.models.UsuarioImpresso.objects.get(
                usuario=self.user, impresso=self.obj_impresso)
            self.context.update({
                'modelo': self.usuario_impresso.modelo.codigo,
            })
            return True
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'mensagem': f"Impresso '{self.impresso}' não cadastrado para o usuário",
            })
            return False

    def print(self, data, field, inicial, final=None, copias=1):
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
        if final is None:
            final = inicial
        try:
            imprime = False
            for row in data:
                if row[field] == inicial:
                    imprime = True
                if imprime:
                    for _ in range(copias):
                        teg.context(row)
                        teg.printer_send()
                    if row[field] == final:
                        break
        except Exception:
            self.context.update({
                'mensagem': f"Erro durante impressão",
            })
            return False
        finally:
            teg.printer_end()

        return True


class EnderecoPrint1(PermissionRequiredMixin, View):

    def __init__(self) -> None:
        self.permission_required = 'cd.imprime_etq_palete'
        self.impresso = 'etiqueta-de-endereco'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        self.data = query_endereco(cursor, 'TO')

        if not next(
            (
                row for row in self.data
                if row["end"] == self.endereco
            ),
            False
        ):
            self.context.update({
                'result': 'ERRO',
                'state': 'Endereço não existe',
            })
            return

        print_label = PrintLabel(self.impresso, self.request.user)
        if print_label.print(self.data, 'end', self.endereco):
            self.context.update({
                'result': 'OK',
                'state': 'OK!',
            })
        else:
            self.context.update({
                'result': 'ERRO',
                'state': print_label.context['mensagem'],
            })
            self.context.update(print_label.context)

    def get(self, request, *args, **kwargs):
        self.request = request
        self.copias = kwargs['copias']
        self.endereco = kwargs['endereco'].upper()
        self.context = {
            'copias': self.copias,
            'endereco': self.endereco,
        }
        self.mount_context()
        return JsonResponse(self.context, safe=False)

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

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        # self.final = self.final.upper()

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
                # 'mensagem': 'Endereço não existe',
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

        print_label = PrintLabel(self.impresso, self.request.user)
        if print_label.print(self.data, 'end', self.inicial):
            self.context.update({
                'mensagem': 'OK!',
            })
        else:
            self.context.update(print_label.context)
