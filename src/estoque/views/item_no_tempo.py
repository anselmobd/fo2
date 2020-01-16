import datetime

from django.db import connections
from django.shortcuts import render
from django.views import View

from utils.views import totalize_data

from estoque import forms
from estoque import queries
from estoque.functions import transfo2_num_doc


class ItemNoTempo(View):

    def __init__(self):
        self.Form_class = forms.ItemNoTempoForm
        self.template_name = 'estoque/item_no_tempo.html'
        self.title_name = 'Item no tempo'

    def mount_context(self, cursor, ref, tam, cor, deposito):
        context = {
            'ref': ref,
            'cor': cor,
            'tam': tam,
            'deposito': deposito,
            }

        dados = queries.item_no_tempo(
            cursor, ref, tam, cor, deposito)

        if len(dados) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'headers': ('Data/hora', 'Quantidade', 'Documento'),
            'fields': ('data', 'qtd', 'doc'),
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
                },
            'dados': dados,
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
            ref = form.cleaned_data['ref']
            cor = form.cleaned_data['cor']
            tam = form.cleaned_data['tam']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, ref, tam, cor, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
