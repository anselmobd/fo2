from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.gtin import gtin13_valid

import produto.forms as forms
import produto.queries as queries


class RefGtinDefine(View):

    def __init__(self):
        self.Form_class = forms.GtinDefineForm
        self.template_name = 'produto/gtin/ref.html'
        self.title_name = 'Busca GTIN'

    def mount_context(self, cursor, ref, tamanho, cor):
        context = {
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
            }

        if ref == '' or \
                tamanho == '' or \
                cor == '':
            context.update({'erro': 'Item não definido'})
            return context

        data = queries.gtin(cursor, ref=ref, tam=tamanho, cor=cor)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'gtin': data[0]['GTIN'],
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
            tamanho = form.cleaned_data['tamanho']
            cor = form.cleaned_data['cor']

            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, ref, tamanho, cor))

        context['form'] = form
        return render(request, self.template_name, context)
