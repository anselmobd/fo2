import datetime
from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.forms.forms2 import PedidoForm2

import lotes.models as models
import lotes.queries as queries


class Historico(View):
    Form_class = PedidoForm2
    template_name = 'lotes/historico.html'
    title_name = 'Histórico de pedido'

    def mount_context(self, cursor, pedido):
        context = {'pedido': pedido}

        data = queries.pedido.ped_inform(cursor, pedido)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
            return context

        data = queries.pedido.historico(pedido)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Histórico não encontrado',
            })
            return context

        context.update({
            'headers': ('Data', 'Usuário',
                        'Máquina', 'Descrição'),
            'fields': ('data_ocorr', 'usuario',
                       'maquina_rede', 'descricao'),
            'pre': ['descricao'],
            'data': data,
        })
        return context

    def get(self, request, *args, **kwargs):
        if 'pedido' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'pedido' in kwargs:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, pedido))
        context['form'] = form
        return render(request, self.template_name, context)
