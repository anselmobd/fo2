import operator
from collections import namedtuple
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import (
    group_rowspan,
    totalize_grouped_data,
)

from cd.classes.endereco import EnderecoCd
from cd.queries.endereco import lotes_em_local


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/novo_modulo/visao_cd.html'
        self.title_name = 'Visão do CD'
        self.DataKey = namedtuple('DataKey', 'espaco espaco_cod bloco')

    def mount_context(self):
        context = {}
        self.cursor = db_cursor_so(self.request)

        ecd = EnderecoCd()
        lotes = lotes_em_local(self.cursor)
        for row in lotes:
            ecd.endereco = row['endereco']
            row.update(ecd.details_dict)

        lotes.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

        dados = {}
        for end in lotes:
            dados_key = self.DataKey(
                espaco=end['espaco'],
                espaco_cod=end['espaco_cod'],
                bloco=end['bloco'],
            )
            if dados_key not in dados:
                dados[dados_key] = {
                    'enderecos': set(),
                    'lotes': set(),
                }
            dados[dados_key]['enderecos'].add(end['endereco'])
            dados[dados_key]['lotes'].add(end['lote'])

        data = []
        for dados_key in dados:
            row = {
                'espaco': dados_key.espaco,
                'bloco': dados_key.bloco,
                'qtd_ends': len(dados[dados_key]['enderecos']),
                'qtd_lotes': len(dados[dados_key]['lotes']),
            }
            row['qtd_ends|LINK'] = reverse(
                'cd:novo_visao_bloco__get', args=[
                    f"{dados_key.espaco_cod}{dados_key.bloco}"
                ])
            data.append(row)

        group = ['espaco']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['qtd_ends', 'qtd_lotes'],
            'count': [],
            'descr': {'espaco': 'Totais:'},
            'global_sum': ['qtd_ends', 'qtd_lotes'],
            'global_descr': {'espaco': 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        fields = {
            'espaco': 'Espaço',
            'bloco': 'Bloco',
            'qtd_ends': 'Qtd. Endereços',
            'qtd_lotes': 'Qtd. lotes',
        }

        context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            'group': group,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
            },
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)
