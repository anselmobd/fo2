from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetPostView

import comercial.forms as forms
import comercial.models as models


def index(request):
    context = {}
    return render(request, 'comercial/index.html', context)


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

            data = models.busca_clientes(cnpj)
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

                data = models.ficha_cliente(cnpj)
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


class VendasPorCor(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(VendasPorCor, self).__init__(*args, **kwargs)
        self.Form_class = forms.VendasPorCorForm
        self.template_name = 'comercial/vendas_cor.html'
        self.title_name = 'Distribuição de vendas por cor'
        self.get_args = ['cnpj']

    def mount_context(self):
        cnpj = self.form.cleaned_data['cnpj']
        self.context.update({
            'cnpj': cnpj,
        })
        cursor = connections['so'].cursor()
        data = models.get_vendas_cor(cursor, cnpj)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma venda encontrada',
            })
        else:
            self.context.update({
                'headers': ['Cor'],
                'fields': ['cor'],
                'data': data,
            })
