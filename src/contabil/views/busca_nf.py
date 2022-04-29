from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.views import group_rowspan

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

        data = busca_nf(cursor, self.ref, self.cor, self.modelo)

        por_pagina = 100
        paginator = Paginator(data, por_pagina)
        try:
            data = paginator.page(self.pagina)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        for row in data:
            if row['pedido'] == 0:
                row['pedido'] = '-'
            else:
                row['pedido|LINK'] = reverse(
                    'producao:pedido__get', args=[row['pedido']])
            row['pedido|GLYPHICON'] = '_'

            row['nf|LINK'] = reverse(
                'contabil:nota_fiscal__get2',
                args=[row['codigo_empresa'], row['nf']],
            )
            row['nf|GLYPHICON'] = '_'

            row['qtd'] = int(row['qtd'])
            row['valor|DECIMALS'] = 2
            row['data'] = row['data'].date()

            row['item'] = f"{row['nivel']}.{row['ref']}.{row['tam']}.{row['cor']}"

        group = ['codigo_empresa', 'nf', 'data', 'cliente']
        group_rowspan(data, group)

        self.context = {
            'por_pagina': por_pagina,
            'ref': self.ref,
            'titulo': self.title_name,
            'headers': [
                'Empr.', 'NF', 'Data', 'Cliente',
                'Item', 'Descrição',
                'Quantidade', 'Valor', 'Pedido'
            ],
            'fields': [
                'codigo_empresa', 'nf', 'data', 'cliente',
                'item', 'narrativa',
                'qtd', 'valor', 'pedido'
            ],
            'data': data,
            'group': group,
            'style': {
                6: 'text-align: right;',
                7: 'text-align: right;',
            },
        }
