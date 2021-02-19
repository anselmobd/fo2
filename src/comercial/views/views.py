from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.functions import untuple_keys_concat
from utils.functions.format import format_cnpj, format_cpf
from utils.views import TableHfs

import comercial.forms as forms
import comercial.queries as queries


def index(request):
    return render(request, 'comercial/index.html')


class FichaCliente(View):
    Form_class = forms.ClienteForm
    template_name = 'comercial/ficha_cliente.html'
    titulo = 'Ficha do Cliente (duplicatas)'

    def get(self, request, *args, **kwargs):
        if 'cnpj' not in kwargs:
            context = {'titulo': self.titulo}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)
        else:
            return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.titulo}
        form = self.Form_class(request.POST)
        if 'cnpj' in kwargs:
            form.data['cnpj'] = kwargs['cnpj']

        context['form'] = form
        if form.is_valid():
            cnpj = form.cleaned_data['cnpj']

            data = queries.busca_clientes(cnpj)
            if len(data) == 0:
                context['conteudo'] = 'nada'
                return render(request, self.template_name, context)


            for row in data:
                row['c_cgc_num'] = row['c_cgc'].strip()
                link = reverse(
                    "comercial:ficha_cliente__get",
                    args=[row['c_cgc_num']],
                )
                if len(row['c_cgc_num']) < 14:
                    row['c_cgc'] = format_cpf(row['c_cgc_num'])
                else:
                    row['c_cgc'] = format_cnpj(row['c_cgc_num'])
                row['c_cgc|LINK'] = link
                row['c_rsoc'] = row['c_rsoc'].strip()

            if len(data) > 1:
                context.update({
                    'conteudo': 'lista',
                    'headers': ['CNPJ', 'Razão Social'],
                    'fields': ['c_cgc', 'c_rsoc'],
                    'data': data,
                })
                return render(request, self.template_name, context)

            context.update({
                'cnpj': data[0]['c_cgc'],
                'cliente': data[0]['c_rsoc'],
            })

            data = queries.ficha_cliente(data[0]['c_cgc_num'])
            if len(data) == 0:
                context['conteudo'] = 'zerado'
                return render(request, self.template_name, context)

            for row in data:
                row['valor|DECIMALS'] = 2
                row['valor_pago|DECIMALS'] = 2
                row['juros|DECIMALS'] = 2
                if row['data_pago'].year == 1899:
                    row['data_pago'] = '-'

            table = TableHfs({
                'duplicata': ['Duplicata'],
                'stat': ['Stat.'],
                'pedido': ['Pedido'],
                'emissao': ['Emissão'],
                'venc_ori': ['Venc. orig.'],
                'vencimento': ['Vencimento'],
                'prorrogado': ['P.'],
                'valor': ['Valor'],
                'quant': ['Quant.'],
                'quant_fat': ['Quant. fat.'],
                'data_pago': ['Pagamento'],
                'valor_pago': ['Valor pago'],
                'juros': ['Juros'],
                'atraso': ['Atraso'],
                'op': ['Op.'],
                'banco': ['Banco'],
                'desconto': ['Desconto'],
                'observacao': ['Observação'],},
                ['header', 'style'],
            )

            headers, fields, _ = table.hfs()
            context.update({
                'conteudo': 'ficha',
                'headers': headers,
                'fields': fields,
                'style': untuple_keys_concat({
                    (8, 9, 10, 12, 13, 14): 'text-align: right;',
                    (2, 4, 5, 6, 7, 11, 15, 16, 17): 'text-align: center;',
                }),
                'data': data,
            })
        return render(request, self.template_name, context)
