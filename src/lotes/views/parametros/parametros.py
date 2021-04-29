from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.views import totalize_grouped_data

import comercial.models

from lotes.views.parametros_functions import *


class MetaGiro(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaGiro, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_giro.html'
        self.title_name = 'Visualiza meta de giro'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        metas = comercial.models.getMetaEstoqueAtual()
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list = calculaMetaGiroMetas(cursor, metas)

        group = ['modelo']
        totalize_grouped_data(metas_list, {
            'group': group,
            'flags': ['NO_TOT_1'],
            'global_sum': ['giro'],
            'sum': ['giro'],
            'count': [],
            'descr': {'modelo': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Modelo', 'Data', 'Venda mensal', 'Lead',
                        'Meta de giro'],
            'fields': ['modelo', 'data', 'venda_mensal', 'lead',
                       'giro'],
            'data': metas_list,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
            'total': metas_list[-1]['giro'],
        })


class MetaTotal(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaTotal, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_total.html'
        self.title_name = 'Visualiza total das metas'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        metas = comercial.models.getMetaEstoqueAtual()
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list, total = calculaMetaTotalMetas(cursor, metas)

        self.context.update({
            'data': metas_list,
            'total': total,
        })
