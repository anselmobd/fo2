import urllib
from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions.gtin import gtin13_valid

import produto.forms as forms
import produto.queries as queries


class GtinDefine(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = forms.GtinDefineForm
        self.Form_class_barras = forms.GtinDefineBarrasForm
        self.template_name = 'produto/gtin/define.html'
        self.title_name = 'Define GTIN'

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

            if not gtin13_valid(gtin):
                context.update({'erro': 'GTIN inválido'})
                return context

            error, error_msg = queries.set_gtin(
                cursor, '1', ref, tamanho, cor, gtin)
            if error:
                if error > 0:
                    context.update({'msg': f'GTIN não alterado'})
                    return context
                else:
                    context.update(
                        {'erro': f'Erro ao atualizar GTIN [{result}]'})
                    return context
            else:
                context.update({'msg': f'GTIN atualizado para {gtin}'})

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
                            if index == len(t_data):
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


class RefGtinDefine(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
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

            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref, tamanho, cor))

        context['form'] = form
        return render(request, self.template_name, context)


class SetGtinDefine(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = forms.GtinDefineBarrasForm
        self.template_name = 'produto/gtin/set.html'
        self.title_name = 'Define GTIN'

    def mount_context(self, cursor, nivel, ref, tamanho, cor, new_gtin):
        context = {
            'nivel': nivel,
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
            'new_gtin': new_gtin,
            }

        data = queries.gtin(cursor, ref=ref, tam=tamanho, cor=cor)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'gtin': data[0]['GTIN'],
        })

        t_data = queries.ref_tamanhos(cursor, ref)
        if len(t_data) != 0:
            index = next(
                (index for (index, d) in enumerate(t_data)
                 if d["TAM"] == tamanho),
                None)
            if index is not None:
                index += 1
                if index == len(t_data):
                    index = 0
                context['prox_tamanho'] = t_data[index]['TAM']

        if new_gtin:
            if not gtin13_valid(new_gtin):
                context.update({'erro': 'Novo GTIN inválido'})
                return context

            error, error_msg = queries.set_gtin(
                cursor, '1', ref, tamanho, cor, new_gtin)
            if error:
                if error > 0:
                    context.update({'msg': f'GTIN não alterado'})
                    return context
                else:
                    context.update(
                        {'erro': f'Erro ao atualizar GTIN [{result}]'})
                    return context
            else:
                context.update({'msg': f'GTIN atualizado'})

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        nivel = kwargs['nivel']
        ref = kwargs['ref']
        tamanho = kwargs['tamanho']
        cor = kwargs['cor']

        form = self.Form_class()
        context['form'] = form

        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(cursor, nivel, ref, tamanho, cor, ''))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        nivel = kwargs['nivel']
        ref = kwargs['ref']
        tamanho = kwargs['tamanho']
        cor = kwargs['cor']

        form = self.Form_class(request.POST)
        if form.is_valid():
            new_gtin = form.cleaned_data['gtin']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, nivel, ref, tamanho, cor, new_gtin))

        context['form'] = form
        return render(request, self.template_name, context)
