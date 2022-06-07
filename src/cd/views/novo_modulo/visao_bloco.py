import operator
from collections import namedtuple
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import (
    group_rowspan,
    totalize_data,
    totalize_grouped_data,
)

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import lotes_em_local


class VisaoBloco(View):

    def __init__(self):
        self.template_name = 'cd/novo_modulo/visao_bloco.html'
        self.title_name = 'Visão do bloco'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        ecd = EnderecoCd()
        lotes = lotes_em_local(self.cursor, bloco=self.bloco)
        for row in lotes:
            ecd.endereco = row['endereco']
            row.update(ecd.details_dict)

        lotes.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

        dados = {}
        for end in lotes:
            if end['endereco'] not in dados:
                dados[end['endereco']] = {
                    'enderecos': set(),
                    'lotes': set(),
                }
            dados[end['endereco']]['lotes'].add(end['lote'])

        data = [
            {
                'endereco': dados_key,
                'qtd_lotes': len(dados[dados_key]['lotes']),
            }
            for dados_key in dados
        ]

        totalize_data(data, {
            'sum': ['qtd_lotes'],
            'count': [],
            'descr': {'endereco': 'Totais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })

        fields = {
            'endereco': 'Endereço',
            'qtd_lotes': 'Qtd. lotes',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
            },
            'bloco': self.bloco,
        })

    def get(self, request, *args, **kwargs):
        self.bloco = kwargs['bloco']
        self.context = {'titulo': self.title_name}
        self.mount_context()
        return render(request, self.template_name, self.context)
