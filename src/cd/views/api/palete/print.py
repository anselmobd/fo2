from pprint import pprint

from django.http import JsonResponse
from django.views import View

import lotes.models

from cd.classes.palete import Plt


class PaletePrint(View):

    def __init__(self) -> None:
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
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'msg_erro': 'Impresso não cadastrado para o usuário',
            })
            return False


    def print(self):
        if all([self.verifica_impresso(),
                self.verifica_usuario_impresso(),]):
            return False

        return True


    def mount_context(self):
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

        if self.print():
            self.context.update({
                'result': 'OK',
            })
        else:
            self.context.update({
                'result': 'ERRO',
            })


    def get(self, request, *args, **kwargs):
        self.code = kwargs['code']
        self.context = {}
        self.mount_context()
        return JsonResponse(self.context, safe=False)
