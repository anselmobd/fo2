import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get import O2BaseGetView
from utils.views import totalize_data

from cd.queries.endereco import conteudo_local


class VisaoBlocoDetalhe(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoBlocoDetalhe, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_bloco_detalhe.html'
        self.title_name = 'Visão detalhada do bloco'
        self.get_args = ['bloco']
        self.get_args2self = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if self.bloco == '0-':
            self.context['bloco'] = 'Paletes não endereçados'
            local_field = 'palete'
        else:
            self.context['bloco'] = f"Bloco {self.bloco}"
            local_field = 'endereco'

        lotes = conteudo_local(self.cursor, bloco=self.bloco, qtd63=True)

        lotes.sort(key=operator.itemgetter(local_field))

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

        totalize_data(dados, {
            'sum': ['lotes', 'itens'],
            'descr': {local_field: 'Totais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })

        fields = {
            local_field: 'Palete' if local_field == 'palete' else 'Endereço',
            'lotes': 'Lotes',
            'itens': 'Itens',
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
