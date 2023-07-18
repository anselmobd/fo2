from pprint import pprint

from utils.classes import TermalPrint

import lotes.models


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
