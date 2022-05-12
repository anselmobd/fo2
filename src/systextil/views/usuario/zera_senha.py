from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from systextil.models.base import Usuario
from systextil.forms.usuario import ZeraSenhaForm



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

        try:
            usuario = Usuario.objects_all.get(
                usuario=self.login, empresa=self.empresa)
        except Usuario.DoesNotExist:
            self.context.update({
                'msg': 'Usuário inexistente',
            })
            return

        self.context.update({
            'msg': f"Confirma zerar senha de {usuario}",
        })
