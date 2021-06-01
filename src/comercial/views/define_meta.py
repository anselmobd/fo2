from datetime import date
from pprint import pprint

from django import forms
from django.db.models import Exists, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from fo2.connections import db_cursor_so

from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetPostView
from geral.functions import has_permission
from o2.views.base.custom import StopStepsException
from utils.functions import safe_cast

import produto.queries
import lotes.views

import comercial.functions
import comercial.models as models
import comercial.queries as queries
from comercial.models.functions.meta_referencia import meta_ref_incluir
from comercial.models.functions.meta_periodos import get_meta_periodos


class DefineMeta(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(DefineMeta, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm2
        self.template_name = 'comercial/define_meta.html'
        self.title_name = 'Define meta de estoque'
        self.get_args = ['modelo']

    def monta_form_define_meta(self):
        # última meta
        meta = models.MetaEstoque.objects.filter(modelo=self.modelo)
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

        venda_mensal = self.context['modelo_ponderado']['data'][0]['ponderada']
        multiplicador = 2

        meta_form = forms.Form()
        meta_form.fields['modelo'] = forms.CharField(
            initial=self.modelo, widget=forms.HiddenInput())
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

    def testa_modelo(self):
        refs = produto.queries.modelo_inform(self.cursor, self.modelo)
        if len(refs) == 0:
            raise StopStepsException('Modelo não encontrado')

    def referencias(self):
        # referencias automaticamente consideradas
        data_ref = queries.pa_de_modelo(self.cursor, self.modelo)

        if len(data_ref) == 0:
            raise StopStepsException('Erro ao pegar PAs de modelo')

        for row in data_ref:
            row['ref|TARGET'] = '_blank'
            row['ref|LINK'] = reverse(
                'produto:ref__get',
                args=[row['ref']],
            )

        return {
            'referencias': {
                'headers': ['Referência'],
                'fields': ['ref'],
                'data': data_ref,
            }
        }

    def ref_incluir(self):
        ref_incl = meta_ref_incluir(self.cursor, self.modelo)
        if ref_incl:
            return {
                'adicionadas': {
                    'headers': ['Referência', 'Informações'],
                    'fields': ['referencia', 'info'],
                    'data': ref_incl,
                },
            }
        return {}

    def inicializacoes_para_grids(self):
        # adicionada coluna de "Venda ponderada" em todas as tabelas
        self.style_pond_meses = {
            **self.meta_periodos['style_meses'],
            self.meta_periodos['n_periodos']+2: 'text-align: right;',
        }

    def get_av_data(self, infor, ref=None, conta_componentes=1):
        if ref is None:
            modelo=self.modelo
        else:
            modelo=None
        av = queries.AnaliseVendas(
            self.cursor,
            ref=ref,
            modelo=modelo,
            infor=infor,
            ordem='infor',
            periodo_cols=self.meta_periodos['cols'],
            qtd_por_mes=True,
            com_venda=False,
            field_ini='',
            )

        for row in av.data:
            for periodo in self.meta_periodos['list']:
                row[periodo['field']] = row[periodo['field']] * conta_componentes

        return av.data

    def calcula_venda_ponderada(self, av_data):
        for row in av_data:
            row['ponderada'] = 0
            for periodo in self.meta_periodos['list']:
                row['ponderada'] += round(
                    row[periodo['field']] 
                    * periodo['peso']
                    * periodo['meses']
                    / self.meta_periodos['tot_peso']
                )

    def pondera_modelo(self):
        av_data = self.get_av_data('modelo')

        if 'adicionadas' in self.context:
            refs_adicionadas = self.context['adicionadas']['data']
            for ref_adicionada in refs_adicionadas:
                if ref_adicionada['ok']:
                    av_ref_data = self.get_av_data(
                        'ref', ref_adicionada['referencia'],
                        ref_adicionada['conta_componentes'])

                    av_row = av_data[0]
                    for row in av_ref_data:
                        for periodo in self.meta_periodos['list']:
                            av_row[periodo['field']] += row[periodo['field']]

        self.calcula_venda_ponderada(av_data)
        
        return {
            'modelo_ponderado': {
                'headers': ['Modelo', 'Venda ponderada',
                            *self.meta_periodos['headers']],
                'fields': ['modelo', 'ponderada',
                        *self.meta_periodos['col_fields']],
                'data': av_data,
                'style': self.style_pond_meses,
            },
            'venda_ponderada': av_data[0]['ponderada'],
        }

    def calcula_grade_tamanho(self, av_data):
        for row in av_data:
            row['grade'] = 0
        if self.context['venda_ponderada'] == 0:
            grade_erro = 0
        else:
            qtds = [row['ponderada'] for row in av_data]
            grade_tam, grade_erro = comercial.functions.grade_minima(qtds, 0.05)
            for i in range(len(av_data)):
                if grade_tam is None:
                    av_data[i]['grade'] = 0
                else:
                    av_data[i]['grade'] = grade_tam[i]
        return grade_erro

    def add_ref_tamanho(self, av_data, ref_adicionada):
        av_ref_data = self.get_av_data(
            'tam', ref_adicionada['referencia'],
            ref_adicionada['conta_componentes'])
        for row in av_ref_data:
            av_row = next(
                item
                for item in av_data
                if item["tam"] == row['tam']
            )
            for periodo in self.meta_periodos['list']:
                av_row[periodo['field']] += row[periodo['field']]

    def pondera_tamanho(self):
        av_data = self.get_av_data('tam')

        self.adiciona_referencias(av_data, self.add_ref_tamanho)

        self.calcula_venda_ponderada(av_data)
        grade_erro = self.calcula_grade_tamanho(av_data)

        return {
            'tamanho_ponderado': {
                'headers': ['Tamanho',
                            'Grade (E:{:.0f}%)'.format(grade_erro * 100),
                            'Venda ponderada',
                            *self.meta_periodos['headers']],
                'fields': ['tam', 'grade', 'ponderada',
                        *self.meta_periodos['col_fields']],
                'data': av_data,
                'style': {
                    ** self.style_pond_meses,
                    self.meta_periodos['n_periodos']+3: 'text-align: right;',
                }
            },
        }

    def calcula_distrubuicao_por_cor(self, av_data):
        for row in av_data:
            if self.context['venda_ponderada'] == 0:
                row['distr'] = 0
            else:
                row['distr'] = round(row['ponderada'] / self.context['venda_ponderada'] * 100)

    def add_ref_cor(self, av_data, ref_adicionada):
        av_ref_data = self.get_av_data(
            'cor', ref_adicionada['referencia'])
        for row in av_ref_data:
            ref_cor = row['cor'].lstrip("0")
            if ref_cor not in ref_adicionada['cores_dict']:
                ref_adicionada['info'] = f"ERRO: FALTA COR '{ref_cor}'; " + ref_adicionada['info']
                continue
            combinacao = ref_adicionada['cores_dict'][ref_cor]
            for cor in combinacao:
                av_row = next(
                    item
                    for item in av_data
                    if item["cor"].lstrip("0") == cor
                )
                for periodo in self.meta_periodos['list']:
                    av_row[periodo['field']] += row[periodo['field']] * combinacao[cor]

    def adiciona_referencias(self, av_data, metodo):
        if 'adicionadas' in self.context:
            refs_adicionadas = self.context['adicionadas']['data']
            for ref_adicionada in refs_adicionadas:
                if ref_adicionada['ok']:
                    metodo(av_data, ref_adicionada)

    def pondera_cor(self):
        av_data = self.get_av_data('cor')

        self.adiciona_referencias(av_data, self.add_ref_cor)

        self.calcula_venda_ponderada(av_data)
        self.calcula_distrubuicao_por_cor(av_data)

        return {
            'cor_ponderada': {
                'headers': ['Cor', 'Distribuição', 'Venda ponderada',
                            *self.meta_periodos['headers']],
                'fields': ['cor', 'distr', 'ponderada',
                        *self.meta_periodos['col_fields']],
                'data': av_data,
                'style': {
                    ** self.style_pond_meses,
                    self.meta_periodos['n_periodos']+3: 'text-align: right;',
                }
            },
        }

    def por_ref(self):
        av_data = self.get_av_data('ref')

        if 'adicionadas' in self.context:
            refs_adicionadas = self.context['adicionadas']['data']
            for ref_adicionada in refs_adicionadas:
                if ref_adicionada['ok']:
                    av_ref_data = self.get_av_data(
                        'ref', ref_adicionada['referencia'],
                        ref_adicionada['conta_componentes'])
                    for row in av_ref_data:
                        av_data.append(row)

        self.calcula_venda_ponderada(av_data)

        return {
            'por_ref': {
                'headers': ['Referência', 'Venda ponderada',
                            *self.meta_periodos['headers']],
                'fields': ['ref', 'ponderada',
                           *self.meta_periodos['col_fields']],
                'data': av_data,
                'style': self.style_pond_meses,
            },
        }

    def mostra_meta(self):
        steps = [
            self.testa_modelo,
            (get_meta_periodos, 'meta_periodos'),
            (self.referencias, 'context'),
            (self.ref_incluir, 'context'),
            self.inicializacoes_para_grids,
            (self.pondera_modelo, 'context'),
            (self.pondera_tamanho, 'context'),
            (self.pondera_cor, 'context'),
            (self.por_ref, 'context'),
            (self.monta_form_define_meta),
        ]

        if not self.do_steps(steps):
            return

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.modelo = self.form.cleaned_data['modelo']
        if 'grava' in self.request.POST:
            self.grava_meta()

        self.context.update({
            'modelo': self.modelo,
        })
        self.mostra_meta()
