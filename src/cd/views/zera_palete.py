from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import lotes.models
import lotes.queries
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais
from cd.queries.endereco import lotes_em_endereco, zera_palete


class ZeraPalete(View):

    def __init__(self):
        self.Form_class = cd.forms.ZeraPaleteForm
        self.template_name = 'cd/zera_palete.html'
        self.title_name = 'Conteúdo'

    def mount_context(self, request, form):
        cursor = db_cursor_so(request)

        confirma = form.cleaned_data['confirma']
        palete = form.cleaned_data['palete'].upper()
        context = {'palete': palete}

        if confirma:

            if confirma == palete:
                # zera_palete(cursor, palete)
                context.update({
                    'erro': 'Confirmado.'})
                return context
            else:
                context.update({
                    'erro': 'Não confirmado.'})
                return context
       
        lotes_end = lotes_em_endereco(cursor, palete)

        if (not lotes_end) or (not lotes_end[0]['lote']):
            context.update({
                'erro': 'Nenhum lote no palete.'})
            return context
        
        context.update({
            'erro': 'Não confirmado.'})
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
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
