from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission

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
# from cd.views.endereco_conteudo_importa import EnderecoImporta


class Endereco(O2BaseGetPostView):  # PermissionRequiredMixin

    def __init__(self, *args, **kwargs):
        super(Endereco, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        # self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco.html'
        self.title_name = 'Endereços'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        data = query_endereco(cursor, self.tipo)

        if has_permission(self.request, 'cd.can_admin_pallet'):
            enderecos = []
            if self.tipo == 'IE':
                enderecos = gera_estantes_enderecos()
            elif self.tipo == 'IQ':
                enderecos = gera_quarto_andar_enderecos()
            elif self.tipo == 'IL':
                enderecos = gera_lateral_enderecos()
            elif self.tipo == 'EL':
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
                    data = query_endereco(cursor, self.tipo)

        self.context.update({
            'quant': len(data),
        })

        data = paginator_basic(data, 50, self.page)

        # if has_permission(self.request, 'cd.can_admin_pallet'):
        #     view_aux = EnderecoImporta()
        #     for row in data.object_list:
        #         row['end_antigo'] = view_aux.end_novo_para_antigo(row['end'])

        if self.tipo in ('TO', 'IT', 'ET'):
            headers = ['Espaço']
            fields = ['espaco']
        else:            
            headers = []
            fields = []
        headers += ["Endereço", "Rota", "Palete"]
        fields += ['end', 'rota', 'palete']

        # if has_permission(self.request, 'cd.can_admin_pallet'):
        #     headers += ["Endereço antigo"]
        #     fields += ['end_antigo']

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
