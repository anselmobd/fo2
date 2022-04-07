from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

import lotes.models
import lotes.queries
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    local_de_lote,
    lotes_em_endereco,
)


class LocalizaLote(View):

    def __init__(self):
        self.Form_class = cd.forms.LocalizaLoteForm
        self.template_name = 'cd/localiza_lote.html'
        self.title_name = 'Localiza lote'

    def mount_context(self, request, form):
        cursor = db_cursor_so(request)

        lote = form.cleaned_data['lote']
        context = {'lote': lote}

        local = local_de_lote(cursor, lote)

        if not local:
            context.update({
                'erro': 'Lote não endereçado.'})
            return context

        if len(local) > 1:
            context.update({
                'varios_locais': True,
                'headers': ['Endereço', 'Palete'],
                'fields': ['endereco', 'palete'],
                'data': local,
            })
            return context

        context.update({
            'endereco': local[0]['endereco'],
            'palete': local[0]['palete'],
        })

        lotes_end = lotes_em_endereco(cursor, local[0]['endereco'])

        context.update({
            'headers': ['Lote', 'OP'],
            'fields': ['lote', 'op'],
            'data': lotes_end,
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
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
