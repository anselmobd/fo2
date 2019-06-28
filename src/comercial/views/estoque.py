from pprint import pprint
from datetime import datetime, timedelta

from django.urls import reverse
from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models
import comercial.queries as queries


class EstoqueDesejado(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(EstoqueDesejado, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/estoque_desejado.html'
        self.title_name = 'Estoque desejado'

    def mount_context_inicial(self):
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        total_data_row = zero_data_row.copy()
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo')
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        'modelo|LINK': reverse(
                            'comercial:estoque_desejado__get',
                            args=[row['modelo']]),
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                total_data_row[periodo['range']] += row['qtd']
        self.context.update({
            'headers': ['Modelo', *[p['descr'] for p in self.periodos]],
            'fields': ['modelo', *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style,
        })

    def mount_context_modelo(self, modref):
        self.context.update({
            'modref': modref,
        })

        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo', modelo=modref)
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        'modelo|LINK': reverse(
                            'comercial:estoque_desejado__get',
                            args=[row['modelo']]),
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
        self.context.update({
            'headers': ['Modelo', *[p['descr'] for p in self.periodos]],
            'fields': ['modelo', *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style,
        })



    def mount_context(self):
        modref = None
        if 'modref' in self.kwargs:
            modref = self.kwargs['modref']

        nfs = list(models.ModeloPassadoPeriodo.objects.filter(
            modelo_id=1).order_by('ordem').values())
        if len(nfs) == 0:
            self.context.update({
                'msg_erro': 'Nenhum período definido',
            })
            return
        self.data_nfs = list(nfs)

        self.periodos = []
        n_mes = 0
        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        self.style = {}
        for i, row in enumerate(self.data_nfs):
            periodo = {
                'range': '{}:{}'.format(n_mes+row['meses'], n_mes),
                'meses': row['meses'],
            }
            n_mes += row['meses']

            mes_fim = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            mes_ini = mes.strftime("%m/%Y")
            mes = dec_month(mes)
            if row['meses'] == 1:
                periodo['descr'] = mes_ini
            else:
                periodo['descr'] = '{} - {}'.format(mes_fim, mes_ini)

            self.style[i+2] = 'text-align: right;'

            self.periodos.append(periodo)

        self.cursor = connections['so'].cursor()

        if modref is None:
            self.mount_context_inicial()
        else:
            self.mount_context_modelo(modref)


class Ponderacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Ponderacao, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/ponderacao.html'
        self.title_name = 'Ponderação a aplicar'

    def mount_context(self):
        nfs = list(models.ModeloPassadoPeriodo.objects.filter(
            modelo_id=1).order_by('ordem').values())
        if len(nfs) == 0:
            self.context.update({
                'msg_erro': 'Nenhum período definido',
            })
            return

        data = list(nfs)

        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        for row in data:
            row['mes_fim'] = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            row['mes_ini'] = mes.strftime("%m/%Y")
            mes = dec_month(mes)

        self.context.update({
            'headers': ('# meses', 'Mês inicial', 'Mês final', 'Peso'),
            'fields': ('meses', 'mes_ini', 'mes_fim', 'peso'),
            'data': data,
        })
