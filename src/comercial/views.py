from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetPostView

import produto.queries

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
        self.get_args = ['ref']

    def mount_context(self):
        # cliente = self.form.cleaned_data['cliente']
        ref = self.form.cleaned_data['ref']
        self.context.update({
            # 'cliente': cliente,
            'ref': ref,
        })
        cursor = connections['so'].cursor()

        if ref == '':
            descricao = ''
        else:
            # Informações básicas
            data = produto.queries.ref_inform(cursor, ref)
            if len(data) == 0:
                context.update({
                    'msg_erro': 'Referência não encontrada',
                })
            else:
                descricao = data[0]['DESCR']
        self.context.update({
            'descricao': descricao,
        })

        periodos = ['3m+', '6m+', '12m+', '24m+']
        periodos_descr = ['3 meses', '6 meses', '1 ano', '2 anos']
        data = []
        zero_data_row = {p: 0 for p in periodos}
        total_data_row = zero_data_row.copy()

        for periodo in periodos:
            data_periodo = models.get_vendas_cor(cursor, ref, periodo=periodo)
            for row in data_periodo:
                data_row = [dr for dr in data if dr['cor'] == row['cor']]
                if len(data_row) == 0:
                    data.append({
                        'cor': row['cor'],
                        **zero_data_row
                    })
                    data_row = data[len(data)-1]
                else:
                    data_row = data_row[0]
                data_row[periodo] = row['qtd']
                total_data_row[periodo] += row['qtd']

        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma venda encontrada',
            })
        else:
            for row in data:
                for periodo in periodos:
                    if total_data_row[periodo] > 0:
                        row[periodo] /= (total_data_row[periodo] / 100)
                    row['{}|DECIMALS'.format(periodo)] = 2

            self.context.update({
                'headers': ['Cor', *periodos_descr],
                'fields': ['cor', *periodos],
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                },
                'data': data,
            })
