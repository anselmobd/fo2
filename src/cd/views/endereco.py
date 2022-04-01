from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from cd.forms.endereco import EnderecoForm
from cd.functions.estante import (
    gera_estantes_enderecos,
    gera_quarto_andar_enderecos,
    gera_lateral_enderecos,
    gera_externos_s_enderecos,
)
from cd.queries.endereco import (
    add_endereco,
    query_endereco,
)


class Endereco(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Endereco, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco.html'
        self.title_name = 'Endereços'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        data = query_endereco(self.tipo)

        enderecos = []
        if self.tipo == 'ES':
            enderecos = gera_estantes_enderecos()
        elif self.tipo == 'QA':
            enderecos = gera_quarto_andar_enderecos()
        elif self.tipo == 'LA':
            enderecos = gera_lateral_enderecos()
        elif self.tipo == 'S':
            enderecos = gera_externos_s_enderecos()

        if enderecos:
            count_add = 0
            for endereco in enderecos:
                if not next(
                    (d for d in data if d['end'] == endereco),
                    False
                ):
                    add_endereco(cursor, endereco)
                    count_add += 1

            if count_add:
                data = query_endereco(self.tipo)

        data = paginator_basic(data, 50, self.page)

        if self.tipo == 'TO':
            headers = ['Espaço']
            fields = ['espaco']
        else:            
            headers = []
            fields = []
        headers += ['Endereço', 'Rota']
        fields += ['end', 'rota']

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
