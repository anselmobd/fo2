from pprint import pprint

from django.views import View

from geral.models import (
    UsuarioPainelModulo,
)
from django.shortcuts import (
    render,
)

from utils.views import group_rowspan


class ResponsavelInformativoView(View):

    def get(self, request, *args, **kwargs):
        fields = [
            'painel_modulo__nome',
            'usuario__first_name',
            'usuario__username',
        ]
        dados = UsuarioPainelModulo.objects.filter(
            painel_modulo__habilitado=True,
            usuario__is_active=True,
            usuario__is_superuser=False,
        ).order_by(
            'painel_modulo__slug', 'usuario__username'
        ).values(*fields)
        group = ['painel_modulo__nome']
        group_rowspan(dados, ['painel_modulo__nome'])
        context = {
            'titulo': 'Responsáveis por informativo',
            'headers': ('Módulo', 'Responsável', 'Login'),
            'fields': fields,
            'group': group,
            'dados': dados,
        }
        return render(
            request, f"geral/responsavel_informativo.html", context)
