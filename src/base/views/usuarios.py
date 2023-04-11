from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from utils.functions.models.dictlist import queryset2dictlist

from base.pages_context import get_current_users_requisicao
from o2.views.base.get import O2BaseGetView


class Usuarios(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Usuarios, self).__init__(*args, **kwargs)
        self.permission_required = 'base.can_visualize_usage_log'
        self.template_name = 'base/usuarios.html'
        self.title_name = 'Usuários conectados'

    def mount_context(self):
        queryset = get_current_users_requisicao()

        data = queryset2dictlist(
            queryset.filter(ip_interno=True).order_by('nome'))
        self.context.update({
            'headers': ['Nome', 'Último login', 'Última ação'],
            'fields': ['nome', 'quando', 'ult_acao'],
            'data': data,
        })

        r_data = queryset2dictlist(
            queryset.filter(ip_interno=False).order_by('nome'))
        self.context.update({
            'r_headers': ['Nome', 'Último login', 'Última ação'],
            'r_fields': ['nome', 'quando', 'ult_acao'],
            'r_data': r_data,
        })
