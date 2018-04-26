from pprint import pprint
from django.shortcuts import render
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
                                'infAdProd', 'EAN', 'Narrativa'),
                    'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD',
                               'INFADPROD', 'EAN', 'NARRATIVA'),
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
            if not data_ate:
                data_ate = data_de

            cursor = connections['so'].cursor()
            data = models.reme_indu(
                cursor, dt_saida_de=data_de, dt_saida_ate=data_ate)
            if len(data) == 0:
                context['erro'] = 'Remessa não encontrada'
            else:
                for row in data:
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
                context.update({
                    'data_de': data_de,
                    'data_ate': data_ate,
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
