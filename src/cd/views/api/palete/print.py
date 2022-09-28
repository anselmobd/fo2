from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from utils.classes import TermalPrint

import lotes.models

from cd.classes.palete import Plt
from cd.queries.palete import query_palete


class PaletePrint(PermissionRequiredMixin, View):

    def __init__(self) -> None:
        self.permission_required = 'cd.can_admin_pallet'
        self.impresso = 'etiqueta-de-palete'

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
                "mensagem": f"Impresso '{self.impresso}'não cadastrado",
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
        except TypeError:
            self.context.update({
                'msg_erro': 'Usuário não logado',
            })
            return False
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'msg_erro': 'Impresso não cadastrado para o usuário',
            })
            return False

    def print(self):
        if not all([
                self.verifica_impresso(),
                self.verifica_usuario_impresso(),]):
            return False

        teg = TermalPrint(
            self.usuario_impresso.impressora_termica.nome,
            file_dir=f"impresso/{self.impresso}/%Y/%m"
        )
        teg.template(self.usuario_impresso.modelo.gabarito, '\r\n')
        teg.printer_start()
        try:
            for row in self.data:
                teg.context(row)
                teg.printer_send(self.copias)
        finally:
            teg.printer_end()


        return True

    def mount_context(self):
        if self.code:
            try:
                code_ok = Plt(self.code).verify()
            except ValueError:
                code_ok = False
            if not code_ok:
                self.context.update({
                    'result': 'ERRO',
                    'state': 'Código inválido',
                })
                return

            self.context.update({
                'code': self.code,
            })

            self.data = [{
                'palete': self.code
            }]

        else:
            self.data = query_palete('N', 'A')
            if not self.data:
                self.context.update({
                    'result': 'ERRO',
                    'state': 'Nada a imprimir',
                })
                return

        if self.print():
            self.context.update({
                'result': 'OK',
                'state': 'OK!',
            })
        else:
            self.context.update({
                'result': 'ERRO',
                'state': 'Erro ao imprimir',
            })

    def get(self, request, *args, **kwargs):
        self.copias = (
            kwargs['copias']
            if 'copias' in kwargs and kwargs['copias']
            else 1
        )
        self.code = kwargs['code'] if 'code' in kwargs else None
        self.context = {}
        self.mount_context()
        return JsonResponse(self.context, safe=False)
