from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.db import connections
from django.views import View

import contabil.forms as forms
import contabil.models as models


def index(request):
    context = {}
    return render(request, 'contabil/index.html', context)


class InfAdProd(View):
    Form_class = forms.InfAdProdForm
    template_name = 'contabil/infadprod.html'
    title_name = 'Itens de pedido'

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.Form_class(request.POST)
        context = {'titulo': self.title_name}
        if form.is_valid():
            pedido = form.cleaned_data['pedido']

            cursor = connections['so'].cursor()
            data = models.infadprod_pro_pedido(cursor, pedido)
            if len(data) == 0:
                context['erro'] = 'Pedido não encontrado'
            else:
                row = data[0]
                context.update({
                    'pedido': pedido,
                    'cliente': row['CLIENTE'],
                    'headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Quantidade',
                                'Ref.Cliente (infAdProd)',
                                'Descr.Cliente (infAdProd)',
                                'EAN', 'Narrativa'),
                    'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD',
                               'INFADPROD', 'DESCRCLI',
                               'EAN', 'NARRATIVA'),
                    'data': data,
                })
        context['form'] = form
        return render(request, self.template_name, context)


class RemessaIndustr(View):
    Form_class = forms.RemessaIndustrForm
    template_name = 'contabil/remeindu.html'
    title_name = 'Remessas para industrialização'

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.Form_class(request.POST)
        context = {'titulo': self.title_name}
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            faccao = form.cleaned_data['faccao']
            cliente = form.cleaned_data['cliente']
            pedido = form.cleaned_data['pedido']
            pedido_cliente = form.cleaned_data['pedido_cliente']
            retorno = form.cleaned_data['retorno']
            detalhe = form.cleaned_data['detalhe']

            cursor = connections['so'].cursor()
            data = models.reme_indu(
                cursor, dt_saida_de=data_de, dt_saida_ate=data_ate,
                faccao=faccao, cliente=cliente,
                pedido=pedido, pedido_cliente=pedido_cliente,
                retorno=retorno, detalhe=detalhe)
            if len(data) == 0:
                context['erro'] = 'Remessa não encontrada'
            else:
                total_pecas = 0
                for row in data:
                    total_pecas += row['QTD']
                    row['DT'] = row['DT'].date()
                    if row['DT_RET'] is None:
                        row['DT_RET'] = '-'
                        row['NF_RET'] = '-'
                        row['QTD_RET'] = '-'
                    else:
                        row['DT_RET'] = row['DT_RET'].date()
                    if row['PED'] == 0:
                        row['PED'] = '-'
                        row['CLI'] = '-'
                    if row['PED_CLI'] is None:
                        row['PED_CLI'] = '-'
                    if row['TAM'] is None:
                        row['TAM'] = '-'
                    row['OP|LINK'] = reverse(
                        'producao:op__get', args=[row['OP']])
                    row['OS|LINK'] = reverse(
                        'producao:os__get', args=[row['OS']])
                    if row['PED'] != '-':
                        row['PED|LINK'] = reverse(
                            'producao:pedido__get', args=[row['PED']])
                context.update({
                    'data_de': data_de,
                    'data_ate': data_ate,
                    'faccao': faccao,
                    'cliente': cliente,
                    'pedido': pedido,
                    'pedido_cliente': pedido_cliente,
                    'retorno': retorno,
                    'detalhe': detalhe,
                    'total_pecas': total_pecas,
                    'headers': ('OP', 'Ref.', 'Cor', 'Tam.', 'OS', 'Quant.',
                                'Data saída', 'NF. saída', 'Facção',
                                'Data retorno', 'NF retorno', 'Quant. retorno',
                                'Pedido', 'Ped. cliente', 'Cliente'),
                    'fields': ('OP', 'REF', 'COR', 'TAM', 'OS', 'QTD',
                               'DT', 'NF', 'FACCAO',
                               'DT_RET', 'NF_RET', 'QTD_RET',
                               'PED', 'PED_CLI', 'CLI'),
                    'data': data,
                })

        context['form'] = form
        return render(request, self.template_name, context)
