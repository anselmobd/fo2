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

    def mount_context(self, cursor, nivel, ref, tam, cor):
        context = {
            'nivel': nivel,
            'ref': ref,
            'tam': tam,
            'cor': cor,
            }

        data = models.por_deposito(cursor, nivel, ref, tam, cor)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'headers': ('Nível', 'Referência', 'Tamanho',
                        'Cor', 'Depósito', 'Quantidade'),
            'fields': ('cditem_nivel99', 'cditem_grupo', 'cditem_subgrupo',
                       'cditem_item', 'deposito', 'qtde_estoque_atu'),
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, nivel, ref, tam, cor))
        context['form'] = form
        return render(request, self.template_name, context)
