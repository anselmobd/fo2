from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from utils.views import totalize_grouped_data, group_rowspan

import insumo.queries as queries


class MapaComprasNecessidadeDetalhe(View):
    template_name = 'insumo/mapa_compras_necessidade_detalhe.html'
    title_name = 'Detalhe de necessidade de insumo em uma semana (novo)'

    def __init__(self, *args, **kwargs):
        super(MapaComprasNecessidadeDetalhe, self).__init__(*args, **kwargs)
        self.new_calc = True

    def mount_context(self, cursor, nivel, ref, cor, tam, semana):
        context = {}

        # Informações gerais
        data_id = queries.insumo_descr(cursor, nivel, ref, cor, tam)

        if len(data_id) == 0:
            context.update({
                'msg_erro': 'Item não encontrado',
            })
            return context

        for row in data_id:
            row['REF'] = row['REF'] + ' - ' + row['DESCR']
            row['COR'] = row['COR'] + ' - ' + row['DESCR_COR']
            if row['TAM'] != row['DESCR_TAM']:
                row['TAM'] = row['TAM'] + ' - ' + row['DESCR_TAM']

        context.update({
            'headers_id': ['Nível', 'Insumo', 'Cor', 'Tamanho', 'Unid.'],
            'fields_id': ['NIVEL', 'REF', 'COR', 'TAM', 'UNID'],
            'data_id': data_id,
        })

        # detalhes da necessidade
        data = queries.insumo_necessidade_detalhe(
            cursor, nivel, ref, cor, tam, semana, new_calc=self.new_calc)

        if len(data) != 0:
            max_digits = 0
            for row in data:
                num_digits = str(row['QTD_INSUMO'])[::-1].find('.')
                max_digits = max(max_digits, num_digits)

            for row in data:
                semana = row['SEMANA'].date()
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
                row['REF'] = row['REF'] + ' - ' + row['DESCR']
                row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])

            group = ['REF', 'DESCR']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD_PRODUTO', 'QTD_INSUMO'],
                'count': [],
                'descr': {'OP': 'Totais:'},
                'flags': ['NO_TOT_1'],
                'global_sum': ['QTD_INSUMO'],
                'global_descr': {'QTD_PRODUTO': 'Total geral:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(data, group)

            for row in data:
                row['QTD_INSUMO|DECIMALS'] = max_digits

            context.update({
                'semana': semana,
                'headers': ['Produto a produzir', 'OP',
                            'Quantidade a produzir', 'Quantidade de insumo'],
                'fields': ['REF', 'OP',
                           'QTD_PRODUTO', 'QTD_INSUMO'],
                'style': {3: 'text-align: right;',
                          4: 'text-align: right;'},
                'group': group,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(
                cursor, kwargs['nivel'], kwargs['ref'],
                kwargs['cor'], kwargs['tam'], kwargs['semana']))
        return render(request, self.template_name, context)
