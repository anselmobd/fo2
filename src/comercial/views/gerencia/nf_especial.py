from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.views import group_rowspan, totalize_grouped_data

from contabil.queries import nf_inform

import comercial.forms
from comercial.queries.gerencia import nf_especial

class NfEspecial(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super(NfEspecial, self).__init__()
        self.permission_required = 'comercial.can_gerenciar_nf_especial'
        self.Form_class = comercial.forms.NfEspecialForm
        self.cleaned_data2self = True
        self.template_name = 'comercial/gerencia/nf_especial.html'
        self.title_name = 'NF especial'


    def mount_nfs_especiais(self):
        dados = nf_especial.get_nfs_especiais(self.cursor)

        for row in dados:
            row['data'] = row['data'].date()

        group = ['nf', 'data']
        totalize_grouped_data(dados, {
            'group': group,
            'sum': ['qtd', 'val_tot'],
            'count': [],
            'descr': {'data': 'Totais:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['qtd', 'val_tot'],
            'global_descr': {'data': 'Totais gerais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        for row in dados:
            row['qtd|DECIMALS'] = 0
            row['val_uni|DECIMALS'] = 2
            row['val_tot|DECIMALS'] = 2

        self.context.update({
            'headers': [
                'NF',
                'Data',
                'Nível',
                'Referência',
                'Tamanho',
                'Cor',
                'Quantidade',
                'Preço',
                'Total',
            ],
            'fields': [
                'nf',
                'data',
                'nivel',
                'ref',
                'tam',
                'cor',
                'qtd',
                'val_uni',
                'val_tot',
            ],
            'style': {
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
            'group': group,
            'data': dados,
        })

    def pre_mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.mount_nfs_especiais()

    def mount_context(self):
        self.context.update({
            'nf': self.nf,
        })

        data = nf_inform.query(self.cursor, self.nf, especiais=True)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nota fiscal não encontrada',
            })
            return

        especial = data[0]['especial'] == 1
        self.context.update({
            'especial': especial,
        })

        mess_error = nf_especial.set_nf_especial(self.cursor, self.nf, not especial)

        if mess_error:
            self.context.update({
                'result': f'Erro: {mess_error}',
            })
            return

        self.mount_nfs_especiais()
        self.context.update({
            'result': 'OK',
        })
