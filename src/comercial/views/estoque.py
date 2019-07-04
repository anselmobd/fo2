from pprint import pprint
from datetime import datetime, timedelta, date
from itertools import combinations_with_replacement, permutations, product

from django.urls import reverse
from django.shortcuts import render
from django.db import connections
from django.views import View
from django import forms
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetView, O2BaseGetPostView
from utils.functions import dec_month, dec_months, safe_cast

import comercial.models as models
import comercial.queries as queries
import comercial.forms as come_forms


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
        metas = metas.filter(meta_estoque__gt=0, antiga=False)
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


class AnaliseModelo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(AnaliseModelo, self).__init__(*args, **kwargs)
        self.Form_class = come_forms.AnaliseModeloForm
        self.template_name = 'comercial/analise_modelo.html'
        self.title_name = 'Análise de modelo'
        self.get_args = ['modelo']

    def mount_context_modelo(self, modelo):
        self.context.update({
            'modelo': modelo,
        })

        # vendas do modelo
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo', modelo=modelo)
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

        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return

        self.context['modelo_ponderado'] = {
            'headers': ['Modelo', 'Venda ponderada',
                        *['{} (P:{})'.format(
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
        total_qtd = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='tam', modelo=modelo,
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
                qtd = round(row['qtd'] * periodo['peso'] / self.tot_peso)
                data_row['qtd'] += qtd
                total_qtd += qtd

        if len(data) == 1 or total_qtd == 0:
            self.context['tamanho_ponderado'] = {
                'headers': ['Tamanho', 'Venda ponderada',
                            *['{} (P:{})'.format(
                                p['descr'], p['peso']
                            ) for p in self.periodos]],
                'fields': ['tam', 'qtd',
                           *[p['range'] for p in self.periodos]],
                'data': data,
                'style': self.style_pond_meses,
            }
        else:
            qtds = [row['qtd'] for row in data]

            def grade_minima(qtds, max_erro):
                total = sum(qtds)
                max_value = 1
                while max_value <= 9:
                    grades = product(
                        range(max_value+1), repeat=len(qtds))
                    best = {'grade': [], 'erro': 1}
                    for grade in grades:
                        if max(grade) < max_value:
                            continue
                        tot_grade = sum(grade)
                        diff = 0
                        for i in range(len(qtds)):
                            qtd_grade = total / tot_grade * grade[i]
                            diff += abs(qtd_grade - qtds[i])
                        if best['erro'] > (diff / total):
                            best['erro'] = diff / total
                            best['grade'] = grade
                    if best['erro'] <= max_erro:
                        break
                    max_value += 1
                return best['grade'], best['erro']

            grade_tam, grade_erro = grade_minima(qtds, 0.05)

            for i in range(len(data)):
                if grade_tam is None:
                    data[i]['grade'] = 0
                else:
                    data[i]['grade'] = grade_tam[i]

            self.context['tamanho_ponderado'] = {
                'headers': ['Tamanho',
                            'Grade (E:{:.0f}%)'.format(grade_erro * 100),
                            'Venda ponderada',
                            *['{} (P:{})'.format(
                                p['descr'], p['peso']
                            ) for p in self.periodos]],
                'fields': ['tam', 'grade', 'qtd',
                           *[p['range'] for p in self.periodos]],
                'data': data,
                'style': {
                    ** self.style_pond_meses,
                    len(self.periodos)+3: 'text-align: right;',
                }
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
                colecao=None, cliente=None, por='cor', modelo=modelo)
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
                qtd = round(row['qtd'] * periodo['peso'] / self.tot_peso)
                data_row['qtd'] += qtd
                total_qtd += qtd

        if len(data) == 1 or total_qtd == 0:
            self.context['cor_ponderada'] = {
                'headers': ['Cor', 'Venda ponderada',
                            *['{} (P:{})'.format(
                                p['descr'], p['peso']
                            ) for p in self.periodos]],
                'fields': ['cor', 'qtd',
                           *[p['range'] for p in self.periodos]],
                'data': data,
                'style': self.style_pond_meses,
            }
        else:
            tot_distr = 0
            max_distr_row = {'distr': 0}
            for row in data:
                row['distr'] = round(row['qtd'] / total_qtd * 100)
                if max_distr_row['distr'] < row['distr']:
                    max_distr_row = row
                tot_distr += row['distr']
            if tot_distr < 100:
                max_distr_row['distr'] += (100 - tot_distr)
            self.context['cor_ponderada'] = {
                'headers': ['Cor', 'Distribuição', 'Venda ponderada',
                            *['{} (P:{})'.format(
                                p['descr'], p['peso']
                            ) for p in self.periodos]],
                'fields': ['cor', 'distr', 'qtd',
                           *[p['range'] for p in self.periodos]],
                'data': data,
                'style': {
                    ** self.style_pond_meses,
                    len(self.periodos)+3: 'text-align: right;',
                }
            }

        # vendas por referência
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='ref', modelo=modelo)
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
                        *['{} (P:{})'.format(
                            p['descr'], p['peso']
                        ) for p in self.periodos]],
            'fields': ['ref', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }

        # Form
        venda_mensal = self.context['modelo_ponderado']['data'][0]['qtd']
        multiplicador = 2

        meta_form = forms.Form()
        meta_form.fields['modelo'] = forms.CharField(
            initial=modelo, widget=forms.HiddenInput())
        meta_form.fields['meta_estoque'] = forms.IntegerField(
            initial=0, widget=forms.HiddenInput())
        meta_form.fields['venda'] = forms.IntegerField(
            required=True, initial=venda_mensal,
            label='Venda mensal')
        meta_form.fields['multiplicador'] = forms.IntegerField(
            required=True, initial=multiplicador,
            label='Multiplicador')

        self.context.update({
            'meta_form': meta_form,
            'venda_mensal': venda_mensal,
            'multiplicador': multiplicador,
        })

        if len(self.context['tamanho_ponderado']['data']) > 1:
            tam_form = forms.Form()
            for row in self.context['tamanho_ponderado']['data']:
                field_name = 'tam_{}'.format(row['tam'])
                tam_form.fields[field_name] = forms.IntegerField(
                    required=True, initial=row['grade'],
                    label=row['tam'])
            self.context.update({
                'tam_form': tam_form,
            })

        if len(self.context['cor_ponderada']['data']) > 1:
            cor_form = forms.Form()
            for row in self.context['cor_ponderada']['data']:
                field_name = 'cor_{}'.format(row['cor'])
                cor_form.fields[field_name] = forms.IntegerField(
                    required=True, initial=row['distr'],
                    label=row['cor'])
            self.context.update({
                'cor_form': cor_form,
            })

        # última meta
        meta = models.MetaEstoque.objects.filter(modelo=modelo)
        meta = meta.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        meta = meta.filter(antiga=False)
        meta = list(meta.values())
        if len(meta) == 1:
            meta = meta[0]
            self.context.update({
                'meta_venda_mensal': meta['venda_mensal'],
                'meta_multiplicador': meta['multiplicador'],
            })

    def grava_meta(self):
        modelo = safe_cast(self.request.POST['modelo'], str, '')
        venda = safe_cast(self.request.POST['venda'], int, 0)
        multiplicador = safe_cast(
            self.request.POST['multiplicador'], float, 0)
        meta_estoque = safe_cast(self.request.POST['meta_estoque'], int, 0)

        tamanhos = {}
        for vari in [key for key in self.request.POST
                     if key.startswith('tam_')]:
            tamanhos[vari[4:]] = safe_cast(self.request.POST[vari], int, 0)

        cores = {}
        for vari in [key for key in self.request.POST
                     if key.startswith('cor_')]:
            cores[vari[4:]] = safe_cast(self.request.POST[vari], int, 0)

        try:
            meta = models.MetaEstoque.objects.get(
                modelo=modelo, data=date.today())
        except models.MetaEstoque.DoesNotExist:
            meta = models.MetaEstoque()
        meta.modelo = modelo
        meta.venda_mensal = venda
        meta.multiplicador = multiplicador
        meta.data = date.today()
        meta.meta_estoque = meta_estoque
        meta.save()

        for tamanho in tamanhos:
            try:
                meta_tamanho = models.MetaEstoqueTamanho.objects.get(
                    meta=meta, tamanho=tamanho)
            except models.MetaEstoqueTamanho.DoesNotExist:
                meta_tamanho = models.MetaEstoqueTamanho()
            meta_tamanho.meta = meta
            meta_tamanho.tamanho = tamanho
            meta_tamanho.quantidade = tamanhos[tamanho]
            meta_tamanho.save()

        for cor in cores:
            try:
                meta_cor = models.MetaEstoqueCor.objects.get(
                    meta=meta, cor=cor)
            except models.MetaEstoqueCor.DoesNotExist:
                meta_cor = models.MetaEstoqueCor()
            meta_cor.meta = meta
            meta_cor.cor = cor
            meta_cor.quantidade = cores[cor]
            meta_cor.save()

    def mount_context(self):
        modelo = self.form.cleaned_data['modelo']
        if 'grava' in self.request.POST:
            self.grava_meta()

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

        self.mount_context_modelo(modelo)


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
