import operator
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get import O2BaseGetView
from utils.views import (
    group_rowspan,
    totalize_grouped_data,
)

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import conteudo_local


class VisaoBlocoLotes(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoBlocoLotes, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_bloco_lotes.html'
        self.title_name = 'Visão detalhada do bloco por lote'
        self.get_args = ['bloco']
        self.get_args2self = True
        self.get_args2context = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if self.bloco == '0-':
            self.context['descr_bloco'] = 'Paletes não endereçados'
            local_field = 'palete'
        else:
            self.context['descr_bloco'] = f"Bloco {self.bloco}"
            local_field = 'endereco'

        ecd = EnderecoCd()
        lotes = conteudo_local(self.cursor, bloco=self.bloco, item_qtd63=True)
        for row in lotes:
            ecd.endereco = row['endereco']
            row.update(ecd.details_dict)

        sort_field = 'order_ap' if local_field == 'endereco' else local_field
        lotes.sort(key=operator.itemgetter(sort_field, 'ref', 'cor', 'ordem_tam', 'op', 'lote'))

        for row in lotes:
            if 'endereco' in row:
                row['endereco|LINK'] = reverse(
                    'cd:visao_bloco_detalhe__get', args=[
                        f"{row['endereco']}"
                    ])

        group = [local_field]
        totalize_grouped_data(lotes, {
            'group': group,
            'sum': ['qtd'],
            'descr': {local_field: 'Totais:'},
            'global_sum': ['qtd'],
            'global_descr': {local_field: 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(lotes, group)

        fields = {
            local_field: 'Palete' if local_field == 'palete' else 'Endereço',
            'ref': 'Referência',
            'cor': 'Cor',
            'tam': 'Tamanho',
            'op': 'OP',
            'lote': 'Lote',
            'qtd': 'Quant.(63)',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': lotes,
            'group': group,
            'style': {
                7: 'text-align: right;',
            },
        })
