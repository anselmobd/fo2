import datetime
from pprint import pprint

from django.conf import settings
from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from base.forms.forms2 import ReferenciaForm2

import produto.queries as queries


class HistNarrativa(View):
    Form_class = ReferenciaForm2
    template_name = 'produto/hist_narrativa.html'
    title_name = 'Histórico de narrativas'

    def mount_context(self, referencia):
        context = {'referencia': referencia}

        cursor = connections['so'].cursor()
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
        if 'referencia' in kwargs:
            form.data['referencia'] = kwargs['referencia']
        if form.is_valid():
            referencia = form.cleaned_data['referencia']
            context.update(self.mount_context(referencia))
        context['form'] = form
        return render(request, self.template_name, context)
