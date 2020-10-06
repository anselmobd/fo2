from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from utils.views import totalize_grouped_data, group_rowspan

import lotes.forms as forms
import lotes.models as models
import lotes.queries as queries


class Expedicao(View):
    Form_class = forms.ExpedicaoForm
    template_name = 'lotes/expedicao.html'
    title_name = 'Expedição'

    def mount_context(
            self, cursor, embarque_de, embarque_ate,
            emissao_de, emissao_ate,
            pedido_tussor, pedido_cliente, cliente,
            deposito, detalhe):
        context = {
            'embarque_de': embarque_de,
            'embarque_ate': embarque_ate,
            'emissao_de': emissao_de,
            'emissao_ate': emissao_ate,
            'pedido_tussor': pedido_tussor,
            'pedido_cliente': pedido_cliente,
            'cliente': cliente,
            'detalhe': detalhe,
            'deposito': deposito,
        }

        if detalhe == 'g':
            data = queries.pedido.grade_expedicao(
                cursor,
                embarque_de=embarque_de,
                embarque_ate=embarque_ate,
                emissao_de=emissao_de,
                emissao_ate=emissao_ate,
                pedido_tussor=pedido_tussor,
                pedido_cliente=pedido_cliente,
                cliente=cliente,
                deposito=deposito,
            )
            if len(data) == 0:
                context.update({
                    'msg_erro': 'Nada selecionado',
                })
                return context

            referencia = None
            grade = []
            quant = 0
            data_refs = []
            data.append({
                'REF': 'ZZZZZ',
                'COR': '-',
                'TAM': '-',
                'QTD': 0,
            })
            qtd_total = 0
            for row in data:
                qtd_total += row['QTD']
                if referencia is not None and referencia != row['REF']:
                    grade.append({
                        'tam': '',
                        'cor': 'Total',
                        'qtd': quant,
                        '|STYLE': 'font-weight: bold;'
                    })
                    data_refs.append({
                        'ref': referencia,
                        'grade': {
                            'headers': ['Tamanho', 'Cor', 'Quantidade'],
                            'fields': ['tam', 'cor', 'qtd'],
                            'data': grade,
                            'style': {3: 'text-align: right;'},
                        }
                    })
                    grade = []
                    quant = 0
                grade.append({
                    'tam': row['TAM'],
                    'cor': row['COR'],
                    'qtd': row['QTD'],
                })
                quant += row['QTD']
                referencia = row['REF']
            context.update({
                'data_refs': data_refs,
                'qtd_total': qtd_total,
            })
            return context

        data = queries.pedido.ped_expedicao(
            cursor,
            embarque_de=embarque_de,
            embarque_ate=embarque_ate,
            emissao_de=emissao_de,
            emissao_ate=emissao_ate,
            pedido_tussor=pedido_tussor,
            pedido_cliente=pedido_cliente,
            cliente=cliente,
            detalhe=detalhe,
            deposito=deposito,
        )
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nada selecionado',
            })
            return context

        qtd_total = 0
        for row in data:
            qtd_total += row['QTD']
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
            row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
            row['PEDIDO_VENDA|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO_VENDA']])
            if detalhe == 'p':
                if row['GTIN_OK'] == 'S':
                    row['GTIN_OK'] = 'Sim'
                else:
                    row['GTIN_OK'] = 'Não'

        if detalhe != 'p':
            group = ['PEDIDO_VENDA', 'PEDIDO_CLIENTE',
                     'DT_EMISSAO', 'DT_EMBARQUE',
                     'CLIENTE']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD'],
                'count': [],
                'descr': {'REF': 'Total:'},
            })
            group_rowspan(data, group)

        headers = ['Pedido Tussor']
        if detalhe == 'p':
            headers.append('GTIN OK')
        headers.append('Pedido cliente')
        headers.append('Data emissão')
        headers.append('Data embarque')
        headers.append('Cliente')
        if detalhe in ('r', 'c'):
            headers.append('Referência')
        if detalhe == 'c':
            headers.append('Cor')
            headers.append('Tamanho')
        headers.append('Quant.')

        fields = ['PEDIDO_VENDA']
        if detalhe == 'p':
            fields.append('GTIN_OK')
        fields.append('PEDIDO_CLIENTE')
        fields.append('DT_EMISSAO')
        fields.append('DT_EMBARQUE')
        fields.append('CLIENTE')
        if detalhe in ('r', 'c'):
            fields.append('REF')
        if detalhe == 'c':
            fields.append('COR')
            fields.append('TAM')
        fields.append('QTD')

        quant_col = 7
        # if detalhe in ('r', 'c'):
        #     quant_col += 0
        if detalhe == 'c':
            quant_col += 2
        style = {quant_col: 'text-align: right;'}

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
            'qtd_total': qtd_total,
        })
        if detalhe != 'p':
            context.update({
                'group': group,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            embarque_de = form.cleaned_data['embarque_de']
            embarque_ate = form.cleaned_data['embarque_ate']
            emissao_de = form.cleaned_data['emissao_de']
            emissao_ate = form.cleaned_data['emissao_ate']
            pedido_tussor = form.cleaned_data['pedido_tussor']
            pedido_cliente = form.cleaned_data['pedido_cliente']
            cliente = form.cleaned_data['cliente']
            deposito = form.cleaned_data['deposito']
            detalhe = form.cleaned_data['detalhe']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, embarque_de, embarque_ate,
                emissao_de, emissao_ate,
                pedido_tussor, pedido_cliente, cliente,
                deposito, detalhe))
        context['form'] = form
        return render(request, self.template_name, context)
