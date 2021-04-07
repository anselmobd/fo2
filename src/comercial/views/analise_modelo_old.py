from pprint import pprint
from datetime import datetime, date
from itertools import product

from django import forms
from django.db.models import Exists, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetPostView
from geral.functions import has_permission
from utils.functions import dec_month, dec_months, safe_cast

import produto.queries
import lotes.views
from produto.forms import ModeloBugForm

import comercial.models as models
import comercial.queries as queries


class AnaliseModeloOld(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(AnaliseModelo, self).__init__(*args, **kwargs)
        # self.Form_class = ModeloForm2
        self.Form_class = ModeloBugForm
        self.template_name = 'comercial/analise_modelo.html'
        self.title_name = 'Define meta de estoque'
        self.get_args = ['modelo', 'rotina_calculo']

    def mount_context_modelo(self, modelo, zerados):
        self.context.update({
            'modelo': modelo,
        })

        refs = produto.queries.modelo_inform(self.cursor, modelo)
        if len(refs) == 0:
            self.context.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return

        # referencias automaticamente consideradas
        data_ref = queries.pa_de_modelo(self.cursor, modelo)
        if len(data_ref) > 0:
            self.context['referencias'] = {
                'headers': ['Referência'],
                'fields': ['ref'],
                'data': data_ref,
            }

        # referências a incluir
        ref_incl = models.MetaModeloReferencia.objects.filter(
            modelo=modelo,
            incl_excl='i',
        ).values('referencia', 'multiplicador')
        if len(ref_incl) == 0:
            refs_incl = None
            mult_incl = None
        else:
            self.context['adicionadas'] = {
                'headers': ['Referência', 'Multiplicador'],
                'fields': ['referencia', 'multiplicador'],
                'data': ref_incl,
            }
            refs_incl = tuple([r['referencia'] for r in ref_incl])
            mult_incl = tuple([r['multiplicador'] for r in ref_incl])

        # vendas do modelo
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=None, periodo=periodo['range'],
                colecao=None, cliente=None, por='modelo', modelo=modelo,
                zerados=zerados
                )  # refs_incl=refs_incl, mult_incl=mult_incl)
            if len(data_periodo) == 0:
                data_periodo = [{'modelo': modelo, 'qtd': 0}]
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
                        *['{} (P:{})'.format(
                            p['descr'], p['peso']
                        ) for p in self.periodos]],
            'fields': ['modelo', 'qtd',
                       *[p['range'] for p in self.periodos]],
            'data': data,
            'style': self.style_pond_meses,
        }
        venda_ponderada = data[0]['qtd']

        # vendas por tamanho
        data = []
        zero_data_row = {p['range']: 0 for p in self.periodos}
        zero_data_row['qtd'] = 0
        zero_data_row['grade'] = 0
        total_qtd = 0
        for periodo in self.periodos:
            if venda_ponderada == 0:
                data_tam = queries.get_modelo_dims(
                    self.cursor,
                    modelo=modelo,
                    get='tam',
                )
                data_periodo = []
                for row_tam in data_tam:
                    data_periodo.append(
                        {'tam': row_tam['TAM'], 'qtd': 0}
                    )
            else:
                data_periodo = queries.get_vendas(
                    self.cursor, ref=None, periodo=periodo['range'],
                    colecao=None, cliente=None, por='tam', modelo=modelo,
                    order_qtd=False, zerados=zerados
                    )  # , refs_incl=refs_incl, mult_incl=mult_incl)
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
            if total_qtd == 0:
                for row in data:
                    row['grade'] = 1
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
            if venda_ponderada == 0:
                data_tam = queries.get_modelo_dims(
                    self.cursor,
                    modelo=modelo,
                    get='cor',
                )
                data_periodo = []
                for row_tam in data_tam:
                    data_periodo.append(
                        {'cor': row_tam['COR'], 'qtd': 0}
                    )
            else:
                data_periodo = queries.get_vendas(
                    self.cursor, ref=None, periodo=periodo['range'],
                    colecao=None, cliente=None, por='cor', modelo=modelo,
                    zerados=zerados
                    )  # refs_incl=refs_incl, mult_incl=mult_incl)
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
            if total_qtd == 0:
                for row in data:
                    row['distr'] = 1
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
            if venda_ponderada == 0:
                data_tam = queries.get_modelo_dims(
                    self.cursor,
                    modelo=modelo,
                    get='ref',
                )
                data_periodo = []
                for row_tam in data_tam:
                    data_periodo.append(
                        {'ref': row_tam['REF'], 'qtd': 0}
                    )
            else:
                data_periodo = queries.get_vendas(
                    self.cursor, ref=None, periodo=periodo['range'],
                    colecao=None, cliente=None, por='ref', modelo=modelo,
                    zerados=zerados
                    )  # refs_incl=refs_incl, mult_incl=mult_incl)
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

        # última meta
        meta = models.MetaEstoque.objects.filter(modelo=modelo)
        meta = meta.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        meta = meta.filter(antiga=False)
        meta_list = list(meta.values())
        tem_meta = len(meta_list) == 1
        if tem_meta:
            meta_list = meta_list[0]

            meta_tamanhos = models.MetaEstoqueTamanho.objects.filter(meta=meta)
            meta_grade_tamanhos = {}
            for tamanho in meta_tamanhos:
                meta_grade_tamanhos[
                    'tam_{}'.format(tamanho.tamanho)] = tamanho.quantidade

            meta_cores = models.MetaEstoqueCor.objects.filter(meta=meta)
            meta_grade_cores = {}
            for cor in meta_cores:
                meta_grade_cores['cor_{}'.format(cor.cor)] = cor.quantidade

            self.context.update({
                'meta_venda_mensal': meta_list['venda_mensal'],
                'meta_multiplicador': meta_list['multiplicador'],
                'meta_meta_estoque': meta_list['meta_estoque'],
                'meta_grade_tamanhos': meta_grade_tamanhos,
                'meta_grade_cores': meta_grade_cores,
            })

        # Form
        self.context.update({
            'pode_gravar': has_permission(
                self.request, 'comercial.can_define_goal'),
        })

        venda_mensal = self.context['modelo_ponderado']['data'][0]['qtd']
        multiplicador = 2

        meta_form = forms.Form()
        meta_form.fields['modelo'] = forms.CharField(
            initial=modelo, widget=forms.HiddenInput())
        meta_form.fields['meta_estoque'] = forms.IntegerField(
            initial=0, widget=forms.HiddenInput())

        if tem_meta:
            val_inicial = meta_list['venda_mensal']
        else:
            val_inicial = venda_mensal
        meta_form.fields['venda'] = forms.IntegerField(
            required=True, initial=val_inicial,
            label='Venda mensal')

        if tem_meta:
            val_inicial = meta_list['multiplicador']
        else:
            val_inicial = multiplicador
        meta_form.fields['multiplicador'] = forms.FloatField(
            required=True, initial=val_inicial,
            label='Multiplicador')

        str_tamanhos = ''
        pond_grade_tamanhos = {}
        tam_form = forms.Form()
        for row in self.context['tamanho_ponderado']['data']:
            str_tamanhos += '{} '.format(row['tam'])
            field_name = 'tam_{}'.format(row['tam'])
            if len(self.context['tamanho_ponderado']['data']) == 1:
                val_inicial = 1
            else:
                val_inicial = row['grade']
            pond_grade_tamanhos[field_name] = val_inicial
            if tem_meta:
                if field_name in meta_grade_tamanhos:
                    val_inicial = meta_grade_tamanhos[field_name]
                else:
                    val_inicial = 0
            tam_form.fields[field_name] = forms.IntegerField(
                required=True, initial=val_inicial,
                label=row['tam'])
        self.context.update({
            'tam_form': tam_form,
        })

        meta_form.fields['str_tamanhos'] = forms.CharField(
            initial=str_tamanhos, widget=forms.HiddenInput())

        pond_grade_cores = {}
        cor_form = forms.Form()
        for row in self.context['cor_ponderada']['data']:
            field_name = 'cor_{}'.format(row['cor'])
            if len(self.context['cor_ponderada']['data']) == 1:
                val_inicial = 1
            else:
                val_inicial = row['distr']
            pond_grade_cores[field_name] = val_inicial
            if tem_meta:
                if field_name in meta_grade_cores:
                    val_inicial = meta_grade_cores[field_name]
                else:
                    val_inicial = 0
            cor_form.fields[field_name] = forms.IntegerField(
                required=True, initial=val_inicial,
                label=row['cor'])
        self.context.update({
            'cor_form': cor_form,
        })

        self.context.update({
            'pond_venda_mensal': venda_mensal,
            'pond_multiplicador': multiplicador,
            'pond_grade_tamanhos': pond_grade_tamanhos,
            'pond_grade_cores': pond_grade_cores,
            'meta_form': meta_form,
            'venda_mensal': venda_mensal,
            'multiplicador': multiplicador,
        })

    def grava_meta(self):
        if not has_permission(self.request, 'comercial.can_define_goal'):
            return
        modelo = safe_cast(self.request.POST['modelo'], str, '')
        venda = safe_cast(self.request.POST['venda'], int, 0)
        multiplicador = safe_cast(
            self.request.POST['multiplicador'], float, 0)
        meta_estoque = safe_cast(self.request.POST['meta_estoque'], int, 0)
        str_tamanhos = safe_cast(self.request.POST['str_tamanhos'], str, '')

        str_tamanhos = str_tamanhos.strip()
        ordem_tamanhos = str_tamanhos.split(' ')

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
            meta_tamanho.ordem = ordem_tamanhos.index(tamanho)
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

        metas = models.getMetaEstoqueAtual().filter(modelo=modelo)
        if len(metas) != 0:
            lotes.views.calculaMetaGiroMetas(self.cursor, metas)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        modelo = self.form.cleaned_data['modelo']
        rotina_calculo = self.form.cleaned_data['rotina_calculo']
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

        self.mount_context_modelo(modelo, zerados=(rotina_calculo=="bug"))
