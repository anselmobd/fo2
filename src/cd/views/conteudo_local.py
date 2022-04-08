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
from cd.queries.endereco import lotes_em_endereco


class ConteudoLocal(View):

    def __init__(self):
        self.Form_class = cd.forms.ConteudoLocalForm
        self.template_name = 'cd/conteudo_palete.html'
        self.title_name = 'Conteúdo'

    def mount_context(self, request, form):
        cursor = db_cursor_so(request)

        codigo = form.cleaned_data['codigo'].upper()
        context = {'endereco': codigo}

        lotes_end = lotes_em_endereco(cursor, codigo)

        if (not lotes_end) or (not lotes_end[0]['lote']):
            context.update({
                'erro': 'Nenhum lote no endereço.'})
            return context

        eh_palete = len(codigo) == 8

        enderecos = set()
        for row in lotes_end:
            row['lote|LINK'] = reverse(
                'cd:localiza_lote',
                args=[row['lote']]
            )
            if row['endereco']:
                enderecos.add(row['endereco'])
            else:
                row['endereco'] = '-'

        context.update({
            'eh_palete': eh_palete,
            'headers': ['Lote', 'OP', 'Endereço' if eh_palete else 'Palete'],
            'fields': ['lote', 'op', 'endereco' if eh_palete else 'palete'],
            'data': lotes_end,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'codigo' in kwargs and kwargs['codigo']:
            return self.post(request, *args, **kwargs)
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        if 'codigo' in kwargs and kwargs['codigo']:
            form = self.Form_class(kwargs)
        else:
            form = self.Form_class(request.POST)
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
