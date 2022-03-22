from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from cd.forms.endereco import EnderecoForm
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
        self.cleaned_data2self = True

    def gera_dict_estantes(self):
        estantes = {
            'A': {
                'len': 28,
            },
            'B': {
                'len': 28,
                'vazio': {
                    (12, 13): (1,)
                }
            },
            'C': {
                'len': 28,
                'vazio': {
                    (12, 13): (1,)
                }
            },
            'D': {
                'len': 28,
                'vazio': {
                    (6, 13, 14, 22): (1, 2, 3)
                }
            },
            'E': {
                'len': 30,
                'vazio': {
                    (13, 14): (1,)
                }
            },
            'F': {
                'len': 30,
                'vazio': {
                    (12, 13): (1,)
                }
            },
            'G': {
                'len': 30,
                'vazio': {
                    (12, 13): (1,)
                }
            },
            'H': {
                'len': 30,
            },
        }
        enderecos = []
        enderecos_vazios = []
        for estante in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            for coluna in range(estantes[estante]['len']):
                for andar in range(1, 4):
                    try:
                        vazio = estantes[estante]['vazio']
                    except KeyError:
                        vazio = {}
                    try:
                        colunas_diferentes = list(vazio.keys())[0]
                    except IndexError:
                        colunas_diferentes = []
                    if coluna in colunas_diferentes:
                        try:
                            andares_vazios = list(vazio.values())[0]
                        except IndexError:
                            andares_vazios = []
                        andar_vazio = andar in andares_vazios
                    else:
                        andar_vazio = False
                    endereco = f"1{estante}{andar:02}{coluna:02}"
                    if andar_vazio:
                        enderecos_vazios.append(endereco)
                    else:
                        enderecos.append(endereco)
        return enderecos

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        data = query_endereco(self.tipo)

        count_add = 0
        if self.tipo == 'ES':
            enderecos = self.gera_dict_estantes()
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
            headers = ['Área']
            fields = ['area']
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
