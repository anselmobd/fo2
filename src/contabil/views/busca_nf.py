from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import contabil.forms as forms
from contabil.queries.busca_nf import busca_nf


class BuscaNF(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(BuscaNF, self).__init__(*args, **kwargs)
        self.Form_class = forms.buscaNFForm
        self.template_name = 'contabil/busca_nf.html'
        self.title_name = 'Busca nota fiscal'
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = busca_nf(cursor, self.ref)
        for row in data:
            if row['pedido'] == 0:
                row['pedido'] = '-'
            else:
                row['pedido|LINK'] = reverse(
                    'producao:pedido__get', args=[row['pedido']])
            row['qtd'] = int(row['qtd'])
            row['valor|DECIMALS'] = 2

        self.context = {
            'ref': self.ref,
            'headers': [
                'NF', 'Cliente',
                'Nível', 'Referência', 'Tamanho', 'Cor', 'Descrição',
                'Quantidade', 'Valor', 'Pedido'
            ],
            'fields': [
                'nf', 'cliente',
                'nivel', 'ref', 'tam', 'cor', 'narrativa',
                'qtd', 'valor', 'pedido'
            ],
            'data': data,
            'style': {
                3: 'text-align: center;',
                4: 'text-align: center;',
                5: 'text-align: center;',
                6: 'text-align: center;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
        }
