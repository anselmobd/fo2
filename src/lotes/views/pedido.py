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
        for row in data:
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
        else:
            context.update({
                'headers': ('Data de emissão',
                            'Cliente', 'Código do pedido no cliente',
                            'Status do pedido', 'Situação da venda'),
                'fields': ('DT_EMISSAO',
                           'CLIENTE', 'PEDIDO_CLIENTE',
                           'STATUS_PEDIDO', 'SITUACAO_VENDA'),
                'data': data,
            })

            # OPs
            o_data = models.ped_op(cursor, pedido)
            for row in o_data:
                row['ORDEM_PRODUCAO|LINK'] = '/lotes/op/{}'.format(
                    row['ORDEM_PRODUCAO'])
                row['REFERENCIA_PECA|LINK'] = '/produto/ref/{}'.format(
                    row['REFERENCIA_PECA'])
                if row['ORDEM_PRINCIPAL'] == 0:
                    row['ORDEM_PRINCIPAL'] == ''
                else:
                    row['ORDEM_PRINCIPAL|LINK'] = '/lotes/op/{}'.format(
                        row['ORDEM_PRINCIPAL'])
            context.update({
                'o_headers': ('OP', 'Tipo', 'Referência',
                              'OP principal', 'Quantidade'),
                'o_fields': ('ORDEM_PRODUCAO', 'TIPO', 'REFERENCIA_PECA',
                             'ORDEM_PRINCIPAL', 'QTD'),
                'o_data': o_data,
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
