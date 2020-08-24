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
    Form_class_barras = forms.GtinDefineBarrasForm
    template_name = 'produto/gtin/define.html'
    title_name = 'Define GTIN'

    def mount_context(self, cursor, tipo, ref, tamanho, cor, gtin):
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

        if tipo == 'busca':
            context.update({
                'gtin': data[0]['GTIN'],
            })

        elif tipo == 'define':
            context.update({
                'gtin': gtin,
            })

            if gtin.startswith('123'):
                context.update({'erro': 'GTIN inválido'})
                return context

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'busca' in request.POST:

            erro = False
            form = self.Form_class(request.POST)
            context.update({'tipo': 'busca'})
            if form.is_valid():
                ref = form.cleaned_data['ref']
                tamanho = form.cleaned_data['tamanho']
                cor = form.cleaned_data['cor']
                cursor = connections['so'].cursor()

                context.update(self.mount_context(
                    cursor, 'busca', ref, tamanho, cor, None))

                erro = 'erro' in context

                if erro:
                    form = self.Form_class(request.POST)
                else:
                    form = self.Form_class_barras()
                    context.update({'tipo': 'define'})

            context['form'] = form
            response = render(request, self.template_name, context)

            if not erro:
                # response.delete_cookie('ref')
                response.set_cookie('ref', ref)
                # response.delete_cookie('tamanho')
                response.set_cookie('tamanho', tamanho)
                # response.delete_cookie('cor')
                response.set_cookie('cor', cor)

        elif 'define' in request.POST:

            erro = False
            form = self.Form_class_barras(request.POST)
            context.update({'tipo': 'define'})
            if form.is_valid():
                gtin = form.cleaned_data['gtin']
                cursor = connections['so'].cursor()

                ref = request.COOKIES.get('ref', '')
                tamanho = request.COOKIES.get('tamanho', '')
                cor = request.COOKIES.get('cor', '')

                context.update(self.mount_context(
                    cursor, 'define', ref, tamanho, cor, gtin))

                erro = 'erro' in context

                if erro:
                    form = self.Form_class_barras(request.POST)
                else:
                    t_data = queries.ref_tamanhos(cursor, ref)
                    if len(t_data) != 0:
                        index = next(
                            (index for (index, d) in enumerate(t_data)
                             if d["TAM"] == tamanho),
                            None)
                        if index is not None:
                            index += 1
                            if index == len(t_data) - 1:
                                index = 0
                            tamanho = t_data[index]['TAM']
                    form = self.Form_class(initial={
                        'ref': ref,
                        'tamanho': tamanho,
                        'cor': cor,
                    })
                    context.update({'tipo': 'busca'})

            context['form'] = form
            response = render(request, self.template_name, context)

        return response
