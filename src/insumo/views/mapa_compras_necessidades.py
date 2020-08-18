import re
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from base.views import O2BaseGetPostView

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
                    'NESS', 'TEMALT'
                ],
                'style': {
                    3: 'text-align: center;',
                    4: 'text-align: center;',
                    6: 'text-align: center;',
                    8: 'text-align: center;',
                    10: 'text-align: right;',
                    20: 'text-align: right;',
                    24: 'text-align: right;',
                    25: 'text-align: right;',
                }
            },
        }

        semana_field = conf[colunas]['semana_field']
        for row in data:
            row[semana_field] = row[semana_field].date()
            if colunas == 't':
                row['NESS'] = row['CCONSUMO_B'] * row['QTD']

        self.context.update({
            'headers': conf[colunas]['headers'],
            'fields': conf[colunas]['fields'],
            'style': conf[colunas]['style'],
            'data': data,
        })


        return self.context
