from operator import itemgetter
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan, totalize_grouped_data

import produto.queries

import insumo.queries as queries


class MapaComprasNecessidadeDetalhe(View):
    template_name = 'insumo/mapa_compras_necessidade_detalhe.html'
    title_name = 'Detalhe de necessidade de insumo em uma semana'

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
        data = queries.mapa_compras_necessidades_especificas(
            cursor, nivel, ref, cor, tam, colunas='t')
        data_sem = [
            r for r in data
            if r['SEM'].strftime('%Y-%m-%d') == semana
        ]

        data_dict = {}
        refs = set()
        for row in data_sem:
            refs.add(row['REF'])
            semana = row['SEM']
            key = (row['REF'], row['OP'])
            if key not in data_dict:
                data_dict[key] = {
                    'QTD_INSUMO': 0,
                    'QTD_PRODUTO': 0,
                }
            rbanho = 1 if row['RBANHO'] == 0 else row['RBANHO']
            data_dict[key]['QTD_INSUMO'] += (
                row['CCONSUMO_B'] * row['QTD'] * rbanho)
            data_dict[key]['QTD_PRODUTO'] += row['QTD']

        ref_informs = produto.queries.nivel_ref_inform(cursor, 1, tuple(refs))

        descrs = {}
        for inform in ref_informs:
            descrs[inform['REF']] = inform['DESCR']

        data = []
        for key in data_dict:
            value = data_dict[key]
            data.append({
                'DESCR': descrs[key[0]],
                'OP': key[1],
                'QTD_INSUMO': value['QTD_INSUMO'],
                'QTD_PRODUTO': value['QTD_PRODUTO'],
                'REF': key[0],
                'SEMANA': semana,
            })

        data = sorted(data, key=itemgetter('REF', 'OP'))

        # detalhes da necessidade
        # data = queries.insumo_necessidade_detalhe(
        #     cursor, nivel, ref, cor, tam, semana, new_calc=self.new_calc)

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
        cursor = db_cursor_so(request)
        context.update(
            self.mount_context(
                cursor, kwargs['nivel'], kwargs['ref'],
                kwargs['cor'], kwargs['tam'], kwargs['semana']))
        return render(request, self.template_name, context)
