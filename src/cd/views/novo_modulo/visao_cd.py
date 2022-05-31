from collections import namedtuple
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

from cd.queries.endereco import data_details_from_end
from cd.queries.novo_modulo.lotes_em_estoque import LotesEmEstoque


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/novo_modulo/visao_cd.html'
        self.title_name = 'Visão do CD'
        self.DataKey = namedtuple('DataKey', 'espaco bloco')

    def mount_context(self):
        context = {}
        self.cursor = db_cursor_so(self.request)

        # enderecos = query_endereco(cursor)
        lotes_em_estoque = LotesEmEstoque(
            self.cursor,
            tipo='i',
            fields_tuple=(
                'tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
                'palete',
                'endereco',
                'rota',
                'estagio',
                'solicitacoes',
            ),
        )
        lotes = lotes_em_estoque.dados()
        lotes = data_details_from_end(lotes, 'endereco')

        dados = {}
        for end in lotes: 
            dados_key = self.DataKey(
                espaco=end['espaco'],
                bloco=end['bloco'],
            )
            if dados_key not in dados:
                dados[dados_key] = {
                    'enderecos': set(),
                    'lotes': set(),
                }
            dados[dados_key]['enderecos'].add(end['endereco'])
            dados[dados_key]['lotes'].add(end['lote'])

        data = [
            {
                'espaco': dados_key.espaco,
                'bloco': dados_key.bloco,
                'qtd_ends': len(dados[dados_key]['enderecos']),
                'qtd_lotes': len(dados[dados_key]['lotes']),
            }
            for dados_key in dados
        ]


        totalize_data(data, {
            'sum': ['qtd_ends', 'qtd_lotes'],
            'count': [],
            'descr': {'espaco': 'Totais:'},
            'row_style': 'font-weight: bold;',
        })

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
