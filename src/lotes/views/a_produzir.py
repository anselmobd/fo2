from pprint import pprint

from django.db import connections
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetView

import comercial.models


class AProduzir(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(AProduzir, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/a_produzir.html'
        self.title_name = 'A produzir por modelo'

    def mount_context(self):
        self.cursor = connections['so'].cursor()

        data = []

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.exclude(multiplicador=0)
        metas = metas.exclude(venda_mensal=0)
        metas = metas.order_by('-meta_estoque').values()

        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                }
                data.append(data_row)
            data_row['meta_estoque'] = row['meta_estoque']

        self.context.update({
            'headers': ['Modelo', 'Meta de estoque'],
            'fields': ['modelo', 'meta_estoque'],
            'data': data,
        })
