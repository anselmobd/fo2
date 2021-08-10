import urllib
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.gtin import gtin13_valid

import produto.classes as classes
import produto.forms as forms
import produto.queries as queries


class SetGtinDefine(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'produto.can_set_gtin'
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
                context['do_next'] = True
                if index == len(t_data):
                    index = 0
                    context['do_next'] = False
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
                        {'erro': f'Erro ao atualizar GTIN [{error_msg}]'})
                    return context
            else:
                context.update({'msg': f'GTIN atualizado'})
                try:
                    last_value = cache.get(f"set_gtin_{self.username}_last_value", '0')
                    cache.set(f"set_gtin_{self.username}_last_value", new_gtin[:-1])
                    diff = int(new_gtin[:-1]) - int(last_value)
                    if abs(diff) == 1:
                        cache.set(f"set_gtin_{self.username}_last_diff", diff)
                except Exception as error:
                    pass


                _ = classes.ObjsProduto(
                    cursor, nivel, ref, tamanho, cor, new_gtin, self.request.user)

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        self.username = self.request.user.username
        context = {'titulo': self.title_name}
        nivel = kwargs['nivel']
        ref = kwargs['ref']
        tamanho = kwargs['tamanho']
        cor = kwargs['cor']
        old_gtin = kwargs.get('old_gtin', None)

        if old_gtin is None:
            form = self.Form_class()
        else:
            last_diff = cache.get(f"set_gtin_{self.username}_last_diff", 1)
            old_gtin = str(int(old_gtin[:-1])+last_diff)
            form = self.Form_class({
                'gtin': old_gtin,
            })
        context['form'] = form

        cursor = db_cursor_so(request)
        context.update(
            self.mount_context(cursor, nivel, ref, tamanho, cor, ''))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.username = self.request.user.username
        context = {'titulo': self.title_name}
        nivel = kwargs['nivel']
        ref = kwargs['ref']
        tamanho = kwargs['tamanho']
        cor = kwargs['cor']

        form = self.Form_class(request.POST)
        if form.is_valid():
            new_gtin = form.cleaned_data['gtin']

            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(cursor, nivel, ref, tamanho, cor, new_gtin))

        context['form'] = form
        return render(request, self.template_name, context)
