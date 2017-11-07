import copy

from django.shortcuts import render
from django.db import connections
from django.views import View

from lotes.forms import PedidoForm
import lotes.models as models


class Pedido(View):
    Form_class = PedidoForm
    template_name = 'lotes/pedido.html'
    title_name = 'Pedido'

    def mount_context(self, cursor, pedido):
        context = {'pedido': pedido}

        # informações gerais
        data = models.ped_inform(cursor, pedido)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
        else:
            context.update({
                'headers': ('Número do pedido', 'Data de emissão',
                            'Cliente', 'Código do pedido no cliente',
                            'Status do pedido'),
                'fields': ('PEDIDO_VENDA', 'DT_EMISSAO',
                           'CLIENTE', 'PEDIDO_CLIENTE', 'STATUS_PEDIDO'),
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, pedido))
        context['form'] = form
        return render(request, self.template_name, context)
