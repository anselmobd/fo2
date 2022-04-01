import operator
import re
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import group_rowspan, totalize_grouped_data

import lotes.models


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/visao_cd.html'
        self.title_name = 'Visão do CD'

    def mount_context(self):
        context = {}

        lotes_recs = lotes.models.Lote.objects.all().exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values(
            'local', 'lote', 'qtd'
        ).order_by('local')
        if len(lotes_recs) == 0:
            return context

        ruas = {}
        for lote in lotes_recs:
            try:
                rua = re.search('^[A-Z]+', lote['local']).group(0)
            except AttributeError:
                rua = '#'
            if rua in ruas:
                ruas[rua]['ends'].add(lote['local'])
                ruas[rua]['qlotes'] += 1
                ruas[rua]['qtdsum'] += lote['qtd']
            else:
                ruas[rua] = {
                    'ends': set([lote['local']]),
                    'qlotes': 1,
                    'qtdsum': lote['qtd'],
                }

        data = [
            {
                'rua': rua,
                'qenderecos': len(ruas[rua]['ends']),
                'qlotes': ruas[rua]['qlotes'],
                'qtdsum': ruas[rua]['qtdsum'],
            }
            for rua in ruas
        ]

        for row in data:
            if row['rua'] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                row['order'] = 1
                row['area'] = 'Estantes'
            elif row['rua'].startswith('QA'):
                row['order'] = 2
                row['area'] = 'Quarto andar'
            elif row['rua'].startswith('LB'):
                row['order'] = 3
                row['area'] = 'Lateral'
            elif (
                    row['rua'].startswith('S') or
                    row['rua'].startswith('Y')
                 ):
                row['order'] = 4
                row['area'] = 'Externo'
            else:
                row['order'] = 5
                row['area'] = 'Indefinido'

        data.sort(key=operator.itemgetter('order', 'rua'))

        headers = ['Área', 'Rua', 'Endereços', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['area', 'rua', 'qenderecos', 'qlotes', 'qtdsum']

        for row in data:
            row['qenderecos|LINK'] = reverse(
                'cd:visao_rua__get', args=[row['rua']])
            row['qlotes|LINK'] = reverse(
                'cd:visao_rua_detalhe__get', args=[row['rua']])

        group = ['area']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['qenderecos', 'qlotes', 'qtdsum'],
            'count': [],
            'descr': {'rua': 'Totais:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['qenderecos', 'qlotes', 'qtdsum'],
            'global_descr': {'rua': 'Totais gerais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'group': group,
            'style': {3: 'text-align: right;',
                      4: 'text-align: right;',
                      5: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)
