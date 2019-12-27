from pprint import pprint

from django.shortcuts import render
from django.views import View

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

            elif len(data) > 1:
                context['conteudo'] = 'lista'
                for row in data:
                    row['CNPJ'] = row['CNPJ'].strip()
                context['data'] = data

            else:
                cnpj = data[0]['CNPJ'].strip()
                cliente = data[0]['CLIENTE'].strip()

                context['conteudo'] = 'ficha'
                if len(cnpj) == 14:
                    context['cnpj'] = '{}/{}-{}'.format(
                        cnpj[0:8],
                        cnpj[8:12],
                        cnpj[12:14])
                else:
                    context['cnpj'] = cnpj
                context['cliente'] = cliente

                data = queries.ficha_cliente(cnpj)
                if len(data) == 0:
                    context['conteudo'] = 'zerado'
                else:
                    formats = {
                        'EMISSAO': '%d/%m/%Y',
                        'VENC_ORI': '%d/%m/%Y',
                        'VENCIMENTO': '%d/%m/%Y',
                        'DATA_PAGO': '%d/%m/%Y',
                    }
                    for row in data:
                        for field in row:
                            if field in formats:
                                if row[field].year == 1899:
                                    row[field] = '-'
                                else:
                                    row[field] = \
                                        ('{:'+formats[field]+'}').format(
                                            row[field])
                    cliente = data[0]
                    context.update({
                        'headers': (
                            'Duplicata',
                            'Stat.',
                            'Pedido',
                            'Emissão',
                            'Venc. Orig.',
                            'Vencimento',
                            'P.',
                            'Valor',
                            'Quant.',
                            'Quant.Fat.',
                            'Pagamento',
                            'Valor pago',
                            'Juros',
                            'Atraso',
                            'OP',
                            'Banco',
                            'Desconto',
                            'Observação',
                            ),
                        'data': data,
                    })
        return render(request, self.template_name, context)
