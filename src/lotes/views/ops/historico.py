import datetime
from pprint import pprint

from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.views import View

import lotes.forms
import lotes.queries.op


class Historico(View):
    Form_class = lotes.forms.OpForm
    template_name = 'lotes/historico_op.html'
    title_name = 'Histórico de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        data = lotes.queries.op.historico_op(cursor, op)
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
        if 'op' in kwargs and kwargs['op'] is not None:
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
        if 'op' in kwargs and kwargs['op'] is not None:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
