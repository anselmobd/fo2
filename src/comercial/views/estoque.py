from pprint import pprint
from datetime import datetime, timedelta
from itertools import combinations_with_replacement, permutations, product

from django.urls import reverse
from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models
import comercial.queries as queries


class AnaliseVendas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(AnaliseVendas, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/analise_vendas.html'
        self.title_name = 'Análise de vendas'

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
                        'modelo|TARGET': '_blank',
                        'modelo|LINK': reverse(
                            'comercial:analise_vendas__get',
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

        # vendas do modelo
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
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
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                data_row['qtd'] += round(
                    row['qtd'] * periodo['peso'] / self.tot_peso)
        self.context['modelo_ponderado'] = {
            'headers': ['Modelo', 'Venda ponderada',
                        *['{}({})'.format(
                            p['descr'], p['peso']
                        ) for p in self.periodos]],
            'fields': ['modelo', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }

        # vendas por tamanho
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        zero_data_row['grade'] = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='tam', modelo=modref,
                order_qtd=False)
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['tam'] == row['tam']),
                    False)
                if not data_row:
                    data_row = {
                        'tam': row['tam'],
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                data_row['qtd'] += round(
                    row['qtd'] * periodo['peso'] / self.tot_peso)
        qtds = [row['qtd'] for row in data]
        qtds_total = sum(qtds)
        pprint(qtds)
        print(qtds_total)

        def grade_minima(total, qtds, erro_otimo, max_erro):
            max_value = 1
            while max_value <= 9:
                grades = product(
                    range(max_value+1), repeat=len(qtds))
                # pprint(list(grades))
                for grade in grades:
                    if max(grade) < max_value:
                        continue
                    pprint(grade)
                    tot_grade = sum(grade)
                    conta_erros = 0
                    diff = 0
                    for i in range(len(qtds)):
                        qtd_grade = total / tot_grade * grade[i]
                        print(qtd_grade)
                        diff += abs(qtd_grade - qtds[i])
                        # diff = abs((qtd_grade / qtds[i]) - 1)
                        # if diff > max_erro:
                        #     print(i, qtd_grade, diff, 'max_erro')
                        #     conta_erros += 1
                        # else:
                        #     print(i, qtd_grade, diff, 'OK')
                        print(diff)
                        if (diff / total) > max_erro:
                            break
                    # if conta_erros == 0:
                    if (diff / total) <= max_erro:
                        return(grade)
                max_value += 1

        grade_tam = grade_minima(qtds_total, qtds, 0.05, 0.09)
        pprint(grade_tam)
        for i in range(len(data)):
            if grade_tam is None:
                data[i]['grade'] = 0
            else:
                data[i]['grade'] = grade_tam[i]
        self.context['tamanho_ponderado'] = {
            'headers': ['Tamanho', 'Grade', 'Venda ponderada',
                        *['{}({})'.format(
                            p['descr'], p['peso']
                        ) for p in self.periodos]],
            'fields': ['tam', 'grade', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }

        # vendas por cor
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        zero_data_row['distr'] = 0
        total_qtd = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='cor', modelo=modref)
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['cor'] == row['cor']),
                    False)
                if not data_row:
                    data_row = {
                        'cor': row['cor'],
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                data_row['qtd'] += round(
                    row['qtd'] * periodo['peso'] / self.tot_peso)
                total_qtd += round(
                    row['qtd'] * periodo['peso'] / self.tot_peso)
        for row in data:
            row['distr'] = round(row['qtd'] / total_qtd * 100)
        self.context['cor_ponderada'] = {
            'headers': ['Cor', 'Distribuição', 'Venda ponderada',
                        *['{}({})'.format(
                            p['descr'], p['peso']
                        ) for p in self.periodos]],
            'fields': ['cor', 'distr', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }

        # vendas por referência
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='ref', modelo=modref)
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['ref'] == row['ref']),
                    False)
                if not data_row:
                    data_row = {
                        'ref': row['ref'],
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                data_row['qtd'] += round(
                    row['qtd'] * periodo['peso'] / self.tot_peso)
        self.context['por_ref'] = {
            'headers': ['Referência', 'Venda ponderada',
                        *[p['descr'] for p in self.periodos]],
            'fields': ['ref', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }

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
        self.tot_peso = 0
        n_mes = 0
        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        self.style = {}
        for i, row in enumerate(self.data_nfs):
            periodo = {
                'range': '{}:{}'.format(
                    n_mes+row['meses'], n_mes),
                'meses': row['meses'],
                'peso': row['peso'],
            }
            n_mes += row['meses']
            self.tot_peso += row['meses'] * row['peso']

            mes_fim = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            mes_ini = mes.strftime("%m/%Y")
            mes = dec_month(mes)
            if row['meses'] == 1:
                periodo['descr'] = mes_ini
            else:
                if mes_ini[-4:] == mes_fim[-4:]:
                    periodo['descr'] = '{} - {}'.format(mes_fim[:2], mes_ini)
                else:
                    periodo['descr'] = '{} - {}'.format(mes_fim, mes_ini)

            self.style[i+2] = 'text-align: right;'

            self.periodos.append(periodo)

        self.style_pond_meses = {
            ** self.style,
            len(self.periodos)+2: 'text-align: right;',
        }

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
