from django.db import connections
from django.shortcuts import render
from django.views import View

from . import forms
from . import models


def index(request):
    context = {}
    return render(request, 'estoque/index.html', context)


class PorDeposito(View):
    Form_class = forms.PorDepositoForm
    template_name = 'estoque/por_deposito.html'
    title_name = 'Estoque por depósito'

    def mount_context(
            self, cursor, nivel, ref, tam, cor, deposito, agrupamento):
        context = {
            'nivel': nivel,
            'ref': ref,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            }

        if agrupamento == 'r':
            group = 'r'
        else:
            group = ''
        data = models.por_deposito(
            cursor, nivel, ref, tam, cor, deposito, zerados=False, group=group)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        if agrupamento == 'r':
            context.update({
                'headers': ('Nível', 'Referência', 'Depósito',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'dep_descr',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
            })
        else:
            context.update({
                'headers': ('Nível', 'Referência', 'Tamanho',
                            'Cor', 'Depósito', 'Quantidade'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'cditem_subgrupo',
                           'cditem_item', 'dep_descr', 'qtd'),
                'style': {6: 'text-align: right;'},
            })
        context.update({
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            agrupamento = form.cleaned_data['agrupamento']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, nivel, ref, tam, cor, deposito, agrupamento))
        context['form'] = form
        return render(request, self.template_name, context)
