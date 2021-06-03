from pprint import pprint
from datetime import datetime

from django.urls import reverse
from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models
from comercial.models.functions.meta_periodos import get_meta_periodos
import comercial.queries as queries


class VendasPorModeloNew(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VendasPorModeloNew, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/vendas_por_modelo.html'
        self.title_name = 'Vendas por modelo'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.meta_periodos = get_meta_periodos()
        
        av = queries.AnaliseVendas(
            self.cursor,
            infor="modelo",
            ordem="infor",
            periodo_cols=self.meta_periodos["cols"],
            qtd_por_mes=True,
            com_venda=True,
            field_ini='',
        )
        # pprint(av.data)

        for row in av.data:
            row["meta"] = " "
            row["data"] = " "
            link = reverse(
                'comercial:define_meta__get',
                args=[row['modelo']],
            )
            row['modelo|TARGET'] = '_blank'
            row['modelo|LINK'] = link
            row['ponderada'] = 0
            for periodo in self.meta_periodos['list']:
                row['ponderada'] += round(
                    row[periodo['field']] 
                    * periodo['peso']
                    * periodo['meses']
                    / self.meta_periodos['tot_peso']
                )

        # pega as metas definidas
        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.order_by('-meta_estoque').values()
        meta_zerada_data = {}
        for row in metas:
            if row['meta_estoque']:
                data_row = next(
                    (dr for dr in av.data if dr['modelo'] == row['modelo']),
                    False)
                if not data_row:
                    link = reverse(
                        'comercial:define_meta__get',
                        args=[row['modelo']],
                    )
                    data_row = {
                        'modelo': row['modelo'],
                        'modelo|TARGET': '_blank',
                        'modelo|LINK': link,
                        'ponderada': 0,
                        **self.meta_periodos["zero_field_row"],
                    }
                    av.data.append(data_row)
                data_row['meta'] = row['meta_estoque']
                data_row['data'] = row['data']
            else:
                meta_zerada_data[row['modelo']] = row['data']

        data = sorted(
            av.data,
            key=lambda k: (
                0 if k['meta'] == ' ' else -k['meta'],
                -k['ponderada'],
            )
        )

        style = {
            2: 'text-align: right;',
            3: 'text-align: center;',
            4: 'text-align: right;',
            5: 'text-align: right;',
            6: 'text-align: right;',
            7: 'text-align: right;',
            8: 'text-align: right;',
        }

        self.context.update({
            'headers': ['Modelo', 'Meta de estoque', 'Data da meta', 'Venda ponderada',
                        *self.meta_periodos['headers']],
            'fields': ['modelo', 'meta', 'data', 'ponderada',
                       *self.meta_periodos['col_fields']],
            'data': data,
            'style': style,
        })
