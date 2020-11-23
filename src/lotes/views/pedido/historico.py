import datetime
from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from base.forms.forms2 import PedidoForm2

import lotes.models as models
import lotes.queries as queries


class Historico(View):
    Form_class = PedidoForm2
    template_name = 'lotes/historico.html'
    title_name = 'Histórico de pedido'

    def mount_context(self, pedido):
        context = {'pedido': pedido}

        data = queries.pedido.historico(pedido)
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            data = [
                {
                    'data_ocorr': datetime.datetime(2020, 11, 23, 11, 38, 21),
                    'usuario': 'ALESSANDRA_COME',
                    'maquina_rede': '192.168.1.174',
                    'long01': '                              CAPA DO PEDIDO DE VENDAS\n\nCLIENTE: 33200056/313-70\nDATA EMBARQUE: 27/01/21\nOBSERVAÇÕES DE PRODUÇÃO: \nNAT. DE OPERAÇÃO: 2\nTRANSPORTADORA: 11874063/1-93\nTIPO FRETE: 1\nEMPRESA: 1\nMOEDA: 0\nCANCELAMENTO: 0\nSTATUS PEDIDO: 0\nSTATUS COMERCIAL: 0\nSTATUS EXPEDIÇÃO: 0\nSITUAÇÃO PEDIDO: 5\nREPRESENTANTE: 23\nADMINISTRADOR: 0\nTIPO COMISSÃO: 2\n% COMIS. REPRES.: 2\n% COMISSÃO (ADMIN): 0\nCONDIÇÃO PAGTO: 99\nENDEREÇO DE ENTREGA: 2\nEND.COBRANÇA: 2\nTABELA PREÇO: 0-0-0\n  1\n  1\n  N\nDATA PREV. RECEB.: \nPORTADOR: 0\n  \n  \nDATA BASE FATUR: '
                },
                {
                    'data_ocorr': datetime.datetime(2020, 11, 23, 11, 39, 1),
                    'usuario': 'ALESSANDRA_COME',
                    'maquina_rede': '192.168.1.174',
                    'long01': '                              CAPA DO PEDIDO DE VENDAS\n\nSITUAÇÃO PEDIDO: 5 - PEDIDO SUSPENSO -> 0 - PEDIDO LIBERADO\n'
                }
            ]
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
            return context

        context.update({
            'headers': ('Data', 'Usuário',
                        'Máquina', 'Descrição'),
            'fields': ('data_ocorr', 'usuario',
                       'maquina_rede', 'long01'),
            'pre': ['long01'],
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
            context.update(self.mount_context(pedido))
        context['form'] = form
        return render(request, self.template_name, context)
