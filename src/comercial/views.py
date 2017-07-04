from django.shortcuts import render
from django.db import connections
from django.views import View

from .forms import ClienteForm
import comercial.models as models


def index(request):
    context = {}
    return render(request, 'comercial/index.html', context)


class FichaCliente(View):
    Form_class = ClienteForm
    template_name = 'comercial/ficha_cliente.html'
    titulo = 'Ficha do Cliente (duplicatas)'

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.titulo}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.titulo}
        form = self.Form_class(request.POST)
        if form.is_valid():
            cnpj9 = form.cleaned_data['cnpj9']
            cnpj4 = form.cleaned_data['cnpj4']
            # nome = form.cleaned_data['nome']

            data = models.ficha_cliente(cnpj9, cnpj4)
            if len(data) == 0:
                context['erro'] = '.'
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
                            row[field] = \
                                ('{:'+formats[field]+'}').format(row[field])
                cliente = data[0]
                context.update({
                    'cnpj': '{}/{}-{}'.format(
                        cliente['CNPJ'][0:8],
                        cliente['CNPJ'][8:12],
                        cliente['CNPJ'][12:14]),
                    'cliente': cliente['CLIENTE'],
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
        context['form'] = form
        return render(request, self.template_name, context)
