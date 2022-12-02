import random
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from systextil.forms.usuario import ZeraSenhaForm
from systextil.models.base import Usuario
from systextil.queries.usuario import muda_senha_usuario



class ZeraSenha(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ZeraSenha, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/usuario/zera_senha.html'
        self.title_name = 'Zera senha'
        self.Form_class = ZeraSenhaForm
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        self.login = self.login.upper()

        try:
            usuario = Usuario.objects_all.get(
                usuario=self.login, empresa=self.empresa)
        except Usuario.DoesNotExist:
            self.context.update({
                'msg': f"Usuário '{self.login}' na empresa '{self.empresa}' inexistente",
            })
            return

        if self.request.POST.get("zera"):
            self.context.update({
                'msg': f"Confirma zerar senha de '{usuario}'?",
                'confirmar': True,
            })

        else:  # confirmado
            senha = str(random.randint(1000, 9999))

            mudou = muda_senha_usuario(
                cursor,
                usuario.empresa,
                usuario.usuario,
                senha,
            )

            if mudou:
                self.context.update({
                    'msg': f"'Zerada' a senha de '{usuario}' para '{senha}'",
                })
            else:
                self.context.update({
                    'msg': f"Erro ao zerar senha de '{usuario}'!",
                })
