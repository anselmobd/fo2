from pprint import pprint
from datetime import datetime, timedelta

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
        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        n_mes = 0
        periodos = []
        periodos_descr = []
        style = {}
        coluna = 2
        for row in self.data_nfs:
            periodos.append(
                ['{}:{}'.format(n_mes+row['meses'], n_mes), row['meses']])
            mes_fim = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            mes_ini = mes.strftime("%m/%Y")
            mes = dec_month(mes)
            if row['meses'] == 1:
                periodos_descr.append(mes_ini)
            else:
                periodos_descr.append('{} - {}'.format(mes_fim, mes_ini))
            n_mes += row['meses']
            style[coluna] = 'text-align: right;'
            coluna += 1

        self.cursor = connections['so'].cursor()

        data = []
        zero_data_row = {p[0]: 0 for p in periodos}
        total_data_row = zero_data_row.copy()
        for periodo in periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo[0], colecao=None,
                cliente=None, por='modelo')
            for row in data_periodo:
                data_row = [dr for dr in data if dr['modelo'] == row['modelo']]
                if len(data_row) == 0:
                    data.append({
                        'modelo': row['modelo'],
                        **zero_data_row
                    })
                    data_row = data[len(data)-1]
                else:
                    data_row = data_row[0]
                data_row[periodo[0]] = round(row['qtd'] / periodo[1])
                total_data_row[periodo[0]] += row['qtd']
        self.context.update({
            'headers': ['Modelo', *periodos_descr],
            'fields': ['modelo', *[p[0] for p in periodos]],
            'data': data,
            'style': style,
        })

    def mount_context_modelo(self, modref):
        self.context.update({
            'modref': modref,
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
