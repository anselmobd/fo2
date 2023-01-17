import operator
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get import O2BaseGetView
from utils.views import totalize_data

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import conteudo_local


class VisaoBloco(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoBloco, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_bloco.html'
        self.title_name = 'Visão do bloco'
        self.get_args = ['bloco']
        self.get_args2self = True
        self.get_args2context = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if self.bloco == '0-':
            self.context['descr_bloco'] = 'Paletes não endereçados'
            local_field = 'palete'
        else:
            if len(self.bloco) == 6:
                self.context['descr_bloco'] = f"Endereço {self.bloco}"
            else:
                self.context['descr_bloco'] = f"Bloco {self.bloco}"
            local_field = 'endereco'

        ecd = EnderecoCd()
        lotes = conteudo_local(self.cursor, bloco=self.bloco, qtd63=True)
        for lote in lotes:
            ecd.endereco = lote['endereco']
            lote.update(ecd.details_dict)

        sort_field = 'order_ap' if local_field == 'endereco' else local_field
        lotes.sort(key=operator.itemgetter(sort_field))

        locais = {}
        for lote in lotes:
            if lote[local_field] not in locais:
                locais[lote[local_field]] = {
                    'lotes': set(),
                    'itens': 0,
                }
            locais[lote[local_field]]['lotes'].add(lote['lote'])
            locais[lote[local_field]]['itens'] += lote['qtd']

        dados = [
            {
                local_field: local,
                'lotes': len(locais[local]['lotes']),
                'itens': locais[local]['itens'],
            }
            for local in locais
        ]

        if local_field == 'endereco':
            for row in dados:
                row['endereco|LINK'] = reverse(
                    'cd:visao_bloco_detalhe__get', args=[
                        f"{row['endereco']}"
                    ])

        totalize_data(dados, {
            'sum': ['lotes', 'itens'],
            'descr': {local_field: 'Totais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })

        fields = {
            local_field: 'Palete' if local_field == 'palete' else 'Endereço',
            'lotes': 'Lotes',
            'itens': 'Itens(63)',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': dados,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
            },
        })
