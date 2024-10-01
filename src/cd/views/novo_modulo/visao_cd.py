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


class VisaoCd(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VisaoCd, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/visao_cd.html'
        self.title_name = 'Visão do CD'
        self.DataKey = namedtuple('DataKey', 'espaco espaco_cod bloco')

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        ecd = EnderecoCd()
        lotes = conteudo_local(self.cursor, qtd63=True)
        if not lotes:
            self.context.update({
                'msgerr': "Nenhum lote encontrado!",
            })
            return
        
        for lote in lotes:
            ecd.endereco = lote['endereco']
            lote.update(ecd.details_dict)

        lotes.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

        blocos = {}
        for lote in lotes:
            bloco = self.DataKey(
                espaco=lote['espaco'],
                espaco_cod=lote['espaco_cod'],
                bloco=lote['bloco'],
            )
            if bloco not in blocos:
                blocos[bloco] = {
                    'enderecos': set(),
                    'lotes': set(),
                    'qtd': 0,
                }
            blocos[bloco]['enderecos'].add(lote['endereco'])
            blocos[bloco]['lotes'].add(lote['lote'])
            blocos[bloco]['qtd'] += lote['qtd']

        dados = []
        for bloco in blocos:
            lote = {
                'espaco': bloco.espaco,
                'bloco': bloco.bloco,
                'qtd_ends': (
                    0 if bloco.bloco == '-'
                    else len(blocos[bloco]['enderecos'])
                ),
                'qtd_lotes': len(blocos[bloco]['lotes']),
                'qtd': blocos[bloco]['qtd'],
            }
            lote['qtd_ends|LINK'] = reverse(
                'cd:novo_visao_bloco__get', args=[
                    f"{bloco.espaco_cod}{bloco.bloco}"
                ])
            lote['qtd_lotes|LINK'] = reverse(
                'cd:visao_bloco_lotes__get', args=[
                    f"{bloco.espaco_cod}{bloco.bloco}"
                ])
            lote['qtd|LINK'] = reverse(
                'cd:visao_bloco_detalhe__get', args=[
                    f"{bloco.espaco_cod}{bloco.bloco}"
                ])
            dados.append(lote)

        group = ['espaco']
        totalize_grouped_data(dados, {
            'group': group,
            'sum': ['qtd_ends', 'qtd_lotes', 'qtd'],
            'descr': {'espaco': 'Totais:'},
            'global_sum': ['qtd_ends', 'qtd_lotes', 'qtd'],
            'global_descr': {'espaco': 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        fields = {
            'espaco': 'Espaço',
            'bloco': 'Bloco',
            'qtd_ends': 'Endereços',
            'qtd_lotes': 'Lotes',
            'qtd': 'Itens',
        }

        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': dados,
            'group': group,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })
