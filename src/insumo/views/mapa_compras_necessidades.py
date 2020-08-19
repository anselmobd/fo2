import re
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from base.views import O2BaseGetPostView
from utils.views import totalize_grouped_data, totalize_data, group_rowspan

import insumo.queries as queries
import insumo.forms as forms


class MapaComprasNecessidades(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(MapaComprasNecessidades, self).__init__(*args, **kwargs)
        self.Form_class = forms.MapaComprasNecessidadesForm
        self.template_name = 'insumo/mapa_compras_necessidades.html'
        self.title_name = 'Necessidade (mapa)'
        self.get_args = ['nivel', 'ref', 'tamanho', 'cor', 'colunas']

    def mount_context(self):
        nivel = self.form.cleaned_data['nivel']
        ref = self.form.cleaned_data['ref']
        tamanho = self.form.cleaned_data['tamanho']
        cor = self.form.cleaned_data['cor']
        colunas = self.form.cleaned_data['colunas']

        if ref == '':
            return
        self.context.update({
            'nivel': nivel,
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
            'colunas': colunas,
        })

        cursor = connections['so'].cursor()

        data = queries.mapa_compras_necessidades_especificas(
            cursor, nivel, ref, cor, tamanho, colunas=colunas)

        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma necessidade de insumos encontrada',
            })
            return self.context

        conf = {
            'm': {
                'semana_field': 'SEMANA_NECESSIDADE',
                'headers': ['Semana', 'Quantidade'],
                'fields': ['SEMANA_NECESSIDADE', 'QTD_INSUMO'],
                'style': {
                    2: 'text-align: right;',
                }
            },
            't': {
                'semana_field': 'SEM',
                'headers': [
                    'Semana', 'OP', 'Alt.', 'Nível', 'Ref.', 'L.Tam.', 'L.Cor',
                    'Est.', 'OS', 'Qtd.',
                    'A.Tam.', 'A.Cor', 'Banho',
                    'C.Seq.', 'C.Nív.', 'C.Ref.', 'C.Tam.', 'C.Cor',
                    'C.Alt.', 'C.Consumo', 'T.Calc.',
                    'Cor', 'Tam', 'Consumo',
                    'Necess.', 'TemAlt.'
                ],
                'fields': [
                    'SEM', 'OP', 'ALT', 'NIV', 'REF', 'LTAM', 'LCOR',
                    'EST', 'OS', 'QTD',
                    'ATAM', 'ACOR', 'RBANHO',
                    'CSEQ', 'CNIV', 'CREF', 'CTAM', 'CCOR',
                    'CALT', 'CCONSUMO', 'TCALC',
                    'CCOR_B', 'CTAM_B', 'CCONSUMO_B',
                    'QTD_INSUMO', 'TEMALT'
                ],
                'style': {
                    3: 'text-align: center;',
                    4: 'text-align: center;',
                    6: 'text-align: center;',
                    8: 'text-align: center;',
                    10: 'text-align: right;',
                    11: 'text-align: center;',
                    20: 'text-align: right;',
                    23: 'text-align: center;',
                    24: 'text-align: right;',
                    25: 'text-align: right;',
                }
            },
        }

        semana_field = conf[colunas]['semana_field']
        for row in data:
            row[semana_field] = row[semana_field].date()

        if colunas == 'm':
            group = []
            totalize_data(data, {
                'sum': ['QTD_INSUMO', ],
                'count': [],
                'descr': {semana_field: 'Totais:'},
                'row_style': 'font-weight: bold;',
            })

        elif colunas == 't':
            for row in data:
                row['QTD_INSUMO'] = row['CCONSUMO_B'] * row['QTD']
                row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])
                row['OP|GLYPHICON'] = '_'

            group = [semana_field]
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD_INSUMO'],
                'count': [],
                'descr': {semana_field: 'Total:'},
                'global_sum': ['QTD_INSUMO'],
                'global_descr': {semana_field: 'Total geral:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(data, group)

            max_digits_qtd = 0
            max_digits_cons = 0
            for row in data:
                num_digits_qtd = str(row['QTD_INSUMO'])[::-1].find('.')
                max_digits_qtd = max(max_digits_qtd, num_digits_qtd)
                num_digits_cons = str(row['CCONSUMO_B'])[::-1].find('.')
                max_digits_cons = max(max_digits_cons, num_digits_cons)

            for row in data:
                row['QTD_INSUMO|DECIMALS'] = max_digits_qtd
                row['CCONSUMO|DECIMALS'] = max_digits_cons
                row['CCONSUMO_B|DECIMALS'] = max_digits_cons

        self.context.update({
            'headers': conf[colunas]['headers'],
            'fields': conf[colunas]['fields'],
            'style': conf[colunas]['style'],
            'group': group,
            'data': data,
        })

        return self.context
