import datetime
from pprint import pprint

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.shortcuts import render
from django.views import View

import lotes.forms
import lotes.queries.op


class Historico(View):
    Form_class = lotes.forms.HistoricoOpForm
    template_name = 'lotes/historico_op.html'
    title_name = 'Histórico de OP'

    def mount_context(self, cursor, op, oc, dia, usuario, descr, page):
        linhas_pagina = 100
        context = {
            'op': op,
            'oc': oc,
            'dia': dia,
            'usuario': usuario,
            'linhas_pagina': linhas_pagina,
        }

        data = lotes.queries.op.historico_op(cursor, op, oc, dia, usuario, descr)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Histórico não encontrado',
            })
            return context

        paginator = Paginator(data, linhas_pagina)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        context.update({
            'headers': [
                'Periodo',
                'OC',
                'Data/hora', 
                'Tipo', 
                'Descrição', 
                'Usuario', 
                'Máquina', 
                'Tela',
            ],
            'fields': [
                'periodo_producao',
                'ordem_confeccao',
                'data_ocorr', 
                'tipo_ocorr', 
                'descricao_historico', 
                'usuario_rede', 
                'maquina_rede', 
                'aplicacao',
            ],
            'pre': [
                'descricao_historico', 
            ],
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
            oc = form.cleaned_data['oc']
            dia = form.cleaned_data['dia']
            usuario = form.cleaned_data['usuario']
            descr = form.cleaned_data['descr']
            page = form.cleaned_data['page']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op, oc, dia, usuario, descr, page))
        context['form'] = form
        return render(request, self.template_name, context)
