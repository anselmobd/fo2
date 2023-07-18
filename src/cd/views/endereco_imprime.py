from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import query_endereco
from cd.views.print_label import PrintLabel


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
        if print_label.print(self.data, 'end', self.endereco, copias=self.copias):
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
        self.copias = int(kwargs['copias'])
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
        self.final = self.final.upper() if self.final else self.inicial

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

        if not next(
            (
                row for row in self.data
                if row["end"] >= self.inicial
                    and row["end"] <= self.final
            ),
            False
        ):
            self.context.update({
                'mensagem': 'Seleção de endereços inicial e final não funcionais',
            })
            return

        print_label = PrintLabel(self.impresso, self.request.user)
        if print_label.print(self.data, 'end', self.inicial, self.final):
            self.context.update({
                'mensagem': 'OK!',
            })
        else:
            self.context.update(print_label.context)
