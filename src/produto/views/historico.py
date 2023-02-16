import datetime
from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2

import produto.queries as queries


class HistNarrativa(View):

    def __init__(self):
        super().__init__()
        self.Form_class = Forms2().Referencia
        self.template_name = 'produto/hist_narrativa.html'
        self.title_name = 'Histórico de narrativas'

    def mount_context(self, cursor, referencia):
        context = {'referencia': referencia}

        data = queries.ref_inform(cursor, referencia)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Referência não encontrada',
            })
            return context

        data = queries.hist_narrativa(referencia)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Histórico não encontrado',
            })
            return context

        context.update({
            'headers': ('Data', 'Usuário',
                        'Tamanho', 'Cor', 'Narrativa'),
            'fields': ('data_ocorr', 'usuario',
                       'tam', 'cor', 'narrativa'),
            'data': data,
        })
        return context

    def get(self, request, *args, **kwargs):
        if 'referencia' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'referencia' in kwargs:
            form.data['referencia'] = kwargs['referencia']
        if form.is_valid():
            referencia = form.cleaned_data['referencia']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, referencia))
        context['form'] = form
        return render(request, self.template_name, context)
