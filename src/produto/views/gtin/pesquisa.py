import urllib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import produto.forms as forms
import produto.queries as queries


class GtinPesquisa(View):
    Form_class = forms.GtinPesquisaForm
    template_name = 'produto/gtin/pesquisa.html'
    title_name = 'GTIN (EAN13)'

    def mount_context(self, cursor, ref, gtin):
        context = {
            'ref': ref,
            'gtin': gtin,
            }

        data = queries.gtin(cursor, ref=ref, gtin=gtin)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['REF|TARGET'] = '_blank'
            row['BAR'] = ''
            row['BAR|GLYPHICON'] = 'glyphicon-barcode'
            row['BAR|LINK'] = '{}?{}'.format(
                reverse('produto:gtin_pesquisa'),
                urllib.parse.urlencode({
                    'ref': row['REF'],
                }))
            if row['GTIN'] == 'SEM GTIN':
                row['QTD'] = ''
            else:
                if row['QTD'] == 1:
                    row['QTD'] = 'Único'
                else:
                    row['QTD|LINK'] = '{}?{}'.format(
                        reverse('produto:gtin_pesquisa'),
                        urllib.parse.urlencode({
                            'gtin': row['GTIN'],
                        }))

        headers = ['Referência', 'GTINs']
        fields = ['REF', 'BAR']
        if ref and not gtin:
            headers = []
            fields = []
        headers.append('Cor')
        fields.append('COR')
        headers.append('Tamanho')
        fields.append('TAM')

        if gtin and not ref:
            context.update({
                'qtd_repetido': data[0]['QTD']
            })
        else:
            headers.append('GTIN')
            fields.append('GTIN')
            headers.append('')
            fields.append('QTD')

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'gtin' in request.GET:
            kwargs['gtin'] = request.GET['gtin']
            return self.post(request, *args, **kwargs)
        elif 'ref' in request.GET:
            kwargs['ref'] = request.GET['ref']
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if 'gtin' in kwargs:
            form.data['gtin'] = kwargs['gtin']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            gtin = form.cleaned_data['gtin']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref, gtin))
        context['form'] = form
        return render(request, self.template_name, context)
