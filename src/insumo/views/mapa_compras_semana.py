from pprint import pprint
from datetime import timedelta

from django.db import connections
from django.shortcuts import render
from django.views import View

import systextil.models

import insumo.queries as queries
from insumo.forms import MapaComprasSemanaForm


class MapaComprasSemana(View):
    Form_class = MapaComprasSemanaForm
    template_name = 'insumo/mapa_compras_semana.html'
    title_name = 'Mapa de compras por semana'

    def mount_context_pre(self, cursor, periodo, qtd_semanas):
        if periodo is None:
            return {}

        if qtd_semanas is None:
            qtd_semanas = 1
        periodo_atual = systextil.models.Periodo.confeccao.filter(
            periodo_producao=periodo
        ).values()
        periodo_ini = 0
        periodo_fim = 0
        if periodo_atual:
            periodo_ini = periodo_atual[0]['data_ini_periodo'].date()
            periodo_ini += timedelta(days=1)
            periodo_fim = periodo_ini+timedelta(weeks=qtd_semanas-1)
        periodo_ini_int = periodo_ini.year*10000 + \
            periodo_ini.month*100 + periodo_ini.day

        context = {'periodo': periodo,
                   'periodo_ini': periodo_ini,
                   'periodo_fim': periodo_fim,
                   'qtd_semanas': qtd_semanas,
                   'periodo_ini_int': periodo_ini_int,
                   }

        return context

    def mount_context(
            self, cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo,
            versao):
        cursor = connections['so'].cursor()
        data = queries.insumos_cor_tamanho_usados(
            cursor, qtd_itens, nivel, uso, insumo)
        refs = []
        for row in data:
            refs.append('{}.{}.{}.{}'.format(
                row['nivel'], row['ref'], row['cor'], row['tam']))

        context = {
            'refs': refs,
            'qtd_itens': qtd_itens,
            'nivel': nivel,
            'uso': uso,
            'insumo': insumo,
            'versao': versao,
        }

        return context

    def get(self, request, *args, **kwargs):
        if 'periodo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            periodo = None
            qtd_semanas = None
            if form.fields['periodo'].initial:
                periodo = form.fields['periodo'].initial
            if form.fields['qtd_semanas'].initial:
                qtd_semanas = form.fields['qtd_semanas'].initial
            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST.copy())
        if 'periodo' in kwargs:
            form.data['periodo'] = kwargs['periodo']
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            qtd_semanas = form.cleaned_data['qtd_semanas']
            qtd_itens = form.cleaned_data['qtd_itens']
            nivel = form.cleaned_data['nivel']
            uso = form.cleaned_data['uso']
            insumo = form.cleaned_data['insumo']
            versao = form.cleaned_data['versao']

            insumo = ' '.join(insumo.strip().upper().split())
            form.data['insumo'] = insumo

            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context.update(self.mount_context(
                cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo,
                versao))
        context['form'] = form
        return render(request, self.template_name, context)
