from pprint import pprint
from datetime import datetime, date
from itertools import combinations_with_replacement, permutations, product

from django.urls import reverse
from django.shortcuts import render
from django.db import connections
from django.views import View
from django import forms
from django.db.models import Exists, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin

from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetView, O2BaseGetPostView
from geral.functions import has_permission
from utils.views import totalize_data
from utils.functions import dec_month, dec_months, safe_cast, dias_uteis_mes

import produto.queries
import lotes.views

import comercial.models as models
import comercial.queries as queries


class AnaliseVendas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(AnaliseVendas, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/analise_vendas.html'
        self.title_name = 'Análise de vendas'

    def mount_context_inicial(self):
        data = []
        zero_data_row = {'meta': ' ', 'data': ' '}
        zero_data_row.update({p['range']: 0 for p in self.periodos})
        total_data_row = zero_data_row.copy()

        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.order_by('-meta_estoque').values()
        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                    'modelo|TARGET': '_blank',
                    'modelo|LINK': reverse(
                        'comercial:analise_modelo__get',
                        args=[row['modelo']]),
                    **zero_data_row
                }
                data.append(data_row)
            data_row['meta'] = row['meta_estoque']
            data_row['data'] = row['data']

        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo'
            )
            for row in data_periodo:
                data_row = next(
                    (dr for dr in data if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        'modelo|TARGET': '_blank',
                        'modelo|LINK': reverse(
                            'comercial:analise_modelo__get',
                            args=[row['modelo']]),
                        **zero_data_row
                    }
                    data.append(data_row)
                data_row[periodo['range']] = round(
                    row['qtd'] / periodo['meses'])
                total_data_row[periodo['range']] += row['qtd']
        self.context.update({
            'headers': ['Modelo', 'Meta de estoque', 'Data da meta',
                        *[p['descr'] for p in self.periodos]],
            'fields': ['modelo', 'meta', 'data',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style,
        })

    def mount_context(self):
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
        self.style = {
            2: 'text-align: right;',
            3: 'text-align: left;',
        }
        for row in self.data_nfs:
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

            self.style[max(self.style.keys())+1] = 'text-align: right;'

            self.periodos.append(periodo)

        self.cursor = connections['so'].cursor()

        self.mount_context_inicial()


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


def grade_meta_estoque(meta):
    grade = {}

    grade['headers'] = ['Cor/Tamanho']
    grade['fields'] = ['cor']
    meta_tamanhos = models.MetaEstoqueTamanho.objects.filter(
        meta=meta).order_by('ordem')
    meta_grade_tamanhos = {}
    tot_tam = 0
    qtd_por_tam = {}
    grade['style'] = {
        1: 'text-align: left;',
    }
    for tamanho in meta_tamanhos:
        if tamanho.quantidade != 0:
            grade['headers'].append(tamanho.tamanho)
            grade['fields'].append(tamanho.tamanho)
            meta_grade_tamanhos[tamanho.tamanho] = tamanho.quantidade
            tot_tam += tamanho.quantidade
            qtd_por_tam[tamanho.tamanho] = 0
            grade['style'][max(grade['style'].keys())+1] = \
                'text-align: right;'
    grade['style'][max(grade['style'].keys())+1] = \
        'text-align: right; font-weight: bold;'

    qtd_por_tam['total'] = meta.meta_estoque

    grade['headers'].append('Total')
    grade['fields'].append('total')
    tot_packs = meta.meta_estoque / tot_tam

    meta_cores = models.MetaEstoqueCor.objects.filter(
        meta=meta).order_by('cor')
    meta_grade_cores = {}
    tot_cor = 0
    for cor in meta_cores:
        meta_grade_cores[cor.cor] = cor.quantidade
        tot_cor += cor.quantidade

    grade['data'] = []
    meta_estoque = 0
    for meta_cor in meta_grade_cores:
        if meta_grade_cores[meta_cor] != 0:
            linha = {
                'cor': meta_cor,
            }
            cor_packs = round(
                tot_packs / tot_cor * meta_grade_cores[meta_cor])
            for meta_tam in meta_grade_tamanhos:
                qtd_cor_tam = cor_packs * meta_grade_tamanhos[meta_tam]
                linha.update({
                    meta_tam: round(qtd_cor_tam),
                })
                qtd_por_tam[meta_tam] += qtd_cor_tam
            linha['total'] = cor_packs * tot_tam
            meta_estoque += linha['total']
            grade['data'].append(linha)
    grade['meta_estoque'] = meta_estoque
    grade['data'].append({
        'cor': 'Total',
        **qtd_por_tam,
        '|STYLE': 'font-weight: bold;',
    })
    return grade


class Metas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Metas, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/metas.html'
        self.title_name = 'Visualiza meta de estoque'

    def mount_context(self):
        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.order_by('-meta_estoque')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list = list(metas.values())
        for meta in metas:
            grade = grade_meta_estoque(meta)

            idx_meta = [idx for idx, item in enumerate(metas_list)
                        if item['modelo'] == meta.modelo][0]
            metas_list[idx_meta].update({
                'grade': grade,
            })

        totalize_data(metas_list, {
            'sum': ['meta_estoque'],
            'count': [],
            'descr': {'modelo': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Modelo', 'Data', 'Venda mensal', 'Multiplicador',
                        'Meta de estoque'],
            'fields': ['modelo', 'data', 'venda_mensal', 'multiplicador',
                       'meta_estoque'],
            'data': metas_list,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
            'total': metas_list[-1]['meta_estoque'],
        })


class VerificaVenda(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VerificaVenda, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/verifica_venda.html'
        self.title_name = 'Verifica estimativa de venda'

    def mount_context(self):
        style = {
            2: 'text-align: right;',
            3: 'text-align: right;',
            4: 'text-align: right;',
            5: 'text-align: right;',
            6: 'text-align: right;',
            7: 'text-align: right;',
        }

        cursor = connections['so'].cursor()

        zero_data_row = {'meta': 0, 'estimada': 0, 'venda': 0, 'venda30': 0}

        total_data_row = {
            '|STYLE': 'font-weight: bold;',
            **zero_data_row,
        }
        total_meta_row = total_data_row.copy()
        total_outros_row = total_data_row.copy()

        total_data_row['modelo'] = \
            'Quantidades totais de faturamentos e estimativa'
        total_meta_row['modelo'] = 'Totais dos modelos com meta'
        total_outros_row['modelo'] = 'Totais dos modelos sem meta'

        data = [total_data_row]
        data_meta = []
        data_outros = []

        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.exclude(multiplicador=0)
        metas = metas.order_by('-venda_mensal', 'modelo').values()

        for row in metas:
            data_row = next(
                (dr for dr in data_meta if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                    **zero_data_row
                }
                data_meta.append(data_row)
            data_row['meta'] = row['venda_mensal']
            total_meta_row['meta'] += row['venda_mensal']

        data_periodo = queries.get_vendas(
            cursor, ref=None, periodo='0:',
            colecao=None, cliente=None, por='modelo'
        )

        u_tot, u_pass, u_today = dias_uteis_mes()
        u_pass = u_pass + u_today
        if u_pass == 0:
            u_pass = 1

        for row in data_periodo:
            tem_meta = True
            data_row = next(
                (dr for dr in data_meta if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                tem_meta = False
                data_row = next(
                    (dr for dr in data_outros
                     if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        **zero_data_row
                    }
                    data_outros.append(data_row)

            data_row['venda'] = row['qtd']
            total_data_row['venda'] += row['qtd']
            if tem_meta:
                total_meta_row['venda'] += row['qtd']
            else:
                total_outros_row['venda'] += row['qtd']

            data_row['estimada'] = round(row['qtd'] / u_pass * u_tot)
            total_data_row['estimada'] += data_row['estimada']
            if tem_meta:
                total_meta_row['estimada'] += data_row['estimada']
            else:
                total_outros_row['estimada'] += data_row['estimada']

        data_periodo = queries.get_vendas(
            cursor, ref=None, ultimos_dias=30,
            colecao=None, cliente=None, por='modelo'
        )

        for row in data_periodo:
            tem_meta = True
            data_row = next(
                (dr for dr in data_meta if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                tem_meta = False
                data_row = next(
                    (dr for dr in data_outros
                     if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    data_row = {
                        'modelo': row['modelo'],
                        **zero_data_row
                    }
                    data_outros.append(data_row)

            data_row['venda30'] = row['qtd']
            total_data_row['venda30'] += row['qtd']
            if tem_meta:
                total_meta_row['venda30'] += row['qtd']
            else:
                total_outros_row['venda30'] += row['qtd']

        data_meta.append(total_meta_row)
        data_outros.append(total_outros_row)

        for data_row in data_meta:
            if data_row['meta'] == 0:
                data_row['variacao'] = ' '
                data_row['variacao30'] = ' '
            else:
                data_row['variacao'] = round(
                    (data_row['estimada'] - data_row['meta']) /
                    data_row['meta'] * 100
                )

                if data_row['variacao'] > 10:
                    data_row['estimada|STYLE'] = 'color: green;'
                    data_row['variacao|STYLE'] = 'color: green;'
                elif data_row['variacao'] < -10:
                    data_row['estimada|STYLE'] = 'color: red;'
                    data_row['variacao|STYLE'] = 'color: red;'

                if data_row['variacao'] > 0:
                    data_row['variacao'] = '+{}'.format(data_row['variacao'])

                data_row['variacao30'] = round(
                    (data_row['venda30'] - data_row['meta']) /
                    data_row['meta'] * 100
                )

                if data_row['variacao30'] > 10:
                    data_row['venda30|STYLE'] = 'color: green;'
                    data_row['variacao30|STYLE'] = 'color: green;'
                elif data_row['variacao30'] < -10:
                    data_row['venda30|STYLE'] = 'color: red;'
                    data_row['variacao30|STYLE'] = 'color: red;'

                if data_row['variacao30'] > 0:
                    data_row['variacao30'] = '+{}'.format(
                        data_row['variacao30'])

        self.context.update({
            't_headers': [' ',
                          'Estimativa de faturamento do mês',
                          'Faturamento do mês', 'Faturamento de 30 dias'],
            't_fields': ['modelo',
                         'estimada', 'venda', 'venda30'],
            't_data': data,
            't_style': style,

            'headers': ['Modelo', 'Venda mensal indicada',
                        'Estimativa de faturamento do mês', '%',
                        'Faturamento do mês',
                        'Faturamento de 30 dias', '%'],
            'fields': ['modelo', 'meta',
                       'estimada', 'variacao', 'venda',
                       'venda30', 'variacao30'],
            'data': data_meta,
            'style': style,
            'u_tot': u_tot,
            'u_pass': u_pass,

            'o_headers': ['Modelo',
                          'Estimativa de faturamento do mês',
                          'Faturamento do mês', 'Faturamento de 30 dias'],
            'o_fields': ['modelo',
                         'estimada', 'venda', 'venda30'],
            'o_data': data_outros,
            'o_style': style,
        })
