import urllib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import produto.forms as forms
import produto.queries as queries


class GtinDefine(View):
    Form_class = forms.GtinDefineForm
    template_name = 'produto/gtin/define.html'
    title_name = 'Define GTIN'

    def mount_context(self, cursor, ref, tamanho, cor):
        context = {
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
            }

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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref, tamanho, cor))
        context['form'] = form
        return render(request, self.template_name, context)
