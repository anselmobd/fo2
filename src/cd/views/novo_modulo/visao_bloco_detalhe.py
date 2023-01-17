import operator
from collections import namedtuple
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


class VisaoBlocoDetalhe(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoBlocoDetalhe, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_bloco_detalhe.html'
        self.title_name = 'Visão detalhada do bloco'
        self.get_args = ['bloco']
        self.get_args2self = True
        self.get_args2context = True
        self.Key = namedtuple('Key', 'local op ref, cor, tam')

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
        lotes.sort(key=operator.itemgetter(sort_field, 'op', 'ref', 'cor', 'ordem_tam'))

        itens = {}
        for lote in lotes:
            item = self.Key(
                local=lote[local_field],
                op=lote['op'],
                ref=lote['ref'],
                cor=lote['cor'],
                tam=lote['tam'],
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
                'ref': item.ref,
                'cor': item.cor,
                'tam': item.tam,
                'lotes': len(itens[item]['lotes']),
                'qtd': itens[item]['qtd'],
            }
            for item in itens
        ]

        for row in dados:
            if 'endereco' in row:
                row['endereco|LINK'] = reverse(
                    'cd:visao_bloco_detalhe__get', args=[
                        f"{row['endereco']}"
                    ])

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
            'ref': 'Referência',
            'cor': 'Cor',
            'tam': 'Tamanho',
            'lotes': 'Lotes',
            'qtd': 'Quant.',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': dados,
            'group': group,
            'style': {
                6: 'text-align: right;',
                7: 'text-align: right;',
            },
        })
