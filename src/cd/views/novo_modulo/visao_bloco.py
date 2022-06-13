import operator
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import lotes_itens_em_local


class VisaoBloco(View):

    def __init__(self):
        self.template_name = 'cd/novo_modulo/visao_bloco.html'
        self.title_name = 'Visão do bloco'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        ecd = EnderecoCd()
        lotes = lotes_itens_em_local(self.cursor, bloco=self.bloco)
        for row in lotes:
            if row['endereco']:
                ecd.endereco = row['endereco']
                row.update(ecd.details_dict)
            else:
                row['endereco'] = row['palete']

        lotes.sort(key=operator.itemgetter('endereco'))

        dados = {}
        for end in lotes:
            if end['endereco'] not in dados:
                dados[end['endereco']] = {
                    'enderecos': set(),
                    'lotes': set(),
                    'qtd_itens': 0,
                }
            dados[end['endereco']]['lotes'].add(end['lote'])
            dados[end['endereco']]['qtd_itens'] += end['qtd']

        data = [
            {
                'endereco': dados_key if dados_key else 'Não endereçado',
                'qtd_lotes': len(dados[dados_key]['lotes']),
                'qtd_itens': dados[dados_key]['qtd_itens'],
            }
            for dados_key in dados
        ]

        totalize_data(data, {
            'sum': ['qtd_lotes', 'qtd_itens'],
            'count': [],
            'descr': {'endereco': 'Totais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })

        fields = {
            'endereco': 'Endereço',
            'qtd_lotes': 'Qtd. lotes',
            'qtd_itens': 'Qtd. itens',
        }
        if self.bloco == '0-':
            fields['endereco'] = 'Palete'

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
            },
            'bloco': 'Não endereçado' if self.bloco == '0-' else self.bloco,
        })

    def get(self, request, *args, **kwargs):
        self.bloco = kwargs['bloco']
        self.context = {'titulo': self.title_name}
        self.mount_context()
        return render(request, self.template_name, self.context)
