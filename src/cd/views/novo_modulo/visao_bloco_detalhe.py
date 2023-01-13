import operator
from collections import namedtuple
from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get import O2BaseGetView
from utils.views import (
    group_rowspan,
    totalize_grouped_data,
)

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import conteudo_local


class VisaoBlocoDetalhe(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoBlocoDetalhe, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_bloco_detalhe.html'
        self.title_name = 'Visão detalhada do bloco'
        self.get_args = ['bloco']
        self.get_args2self = True
        self.Key = namedtuple('Key', 'local op item')

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if self.bloco == '0-':
            self.context['bloco'] = 'Paletes não endereçados'
            local_field = 'palete'
        else:
            self.context['bloco'] = f"Bloco {self.bloco}"
            local_field = 'endereco'

        ecd = EnderecoCd()
        lotes = conteudo_local(self.cursor, bloco=self.bloco, item_qtd63=True)
        for row in lotes:
            ecd.endereco = row['endereco']
            row.update(ecd.details_dict)

        sort_field = 'order_ap' if local_field == 'endereco' else local_field
        lotes.sort(key=operator.itemgetter(sort_field, 'op', 'ref', 'cor', 'tam'))

        itens = {}
        for lote in lotes:
            item = self.Key(
                local=lote[local_field],
                op=lote['op'],
                item=lote['item'],
            )
            if item not in itens:
                itens[item] = {
                    'lotes': set(),
                    'qtd': 0,
                }
            itens[item]['lotes'].add(lote['lote'])
            itens[item]['qtd'] += lote['qtd']

        dados = [
            {
                local_field: item.local,
                'op': item.op,
                'item': item.item,
                'lotes': len(itens[item]['lotes']),
                'qtd': itens[item]['qtd'],
            }
            for item in itens
        ]

        group = [local_field]
        totalize_grouped_data(dados, {
            'group': group,
            'sum': ['lotes', 'qtd'],
            'count': [],
            'descr': {local_field: 'Totais:'},
            'global_sum': ['lotes', 'qtd'],
            'global_descr': {local_field: 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        fields = {
            local_field: 'Palete' if local_field == 'palete' else 'Endereço',
            'op': 'OP',
            'item': 'Item',
            'lotes': 'Lotes',
            'qtd': 'Quant.',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': dados,
            'group': group,
            'style': {
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })
