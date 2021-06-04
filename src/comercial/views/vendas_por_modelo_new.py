from pprint import pprint
from datetime import datetime

from django.urls import reverse
from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import dec_month, dec_months

import comercial.models as models
import comercial.queries as queries
from comercial.models.functions.meta_periodos import get_meta_periodos
from comercial.models.functions.meta_referencia import meta_ref_incluir


class VendasPorModeloNew(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(VendasPorModeloNew, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/vendas_por_modelo.html'
        self.title_name = 'Vendas por modelo'

    def get_av(self):
        self.av = queries.AnaliseVendas(
            self.cursor,
            infor="modelo",
            ordem="infor",
            periodo_cols=self.meta_periodos["cols"],
            qtd_por_mes=True,
            com_venda=True,
            field_ini='',
        )

    def calc_ponderada(self):
        for row in self.av.data:
            row['ponderada'] = 0
            for periodo in self.meta_periodos['list']:
                row['ponderada'] += round(
                    row[periodo['field']] 
                    * periodo['peso']
                    * periodo['meses']
                    / self.meta_periodos['tot_peso']
                )

    def get_metas(self):
        metas = models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        return metas.filter(antiga=False).values()

    def inclui_referencias_adicionadas(self, data_row):
        ref_incl = meta_ref_incluir(self.cursor, data_row['modelo'])
        queries.AnaliseVendasComKits(
            self.cursor, self.meta_periodos,
            ref_incl, 'modelo',
            modelo=data_row['modelo'],
            data=[data_row],
        ).get_data()

    def insere_metas(self):
        for row in self.av.data:
            row["meta"] = " "
            row["data"] = " "
        for row in self.get_metas():
            data_row = next(
                (dr for dr in self.av.data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                    'ponderada': 0,
                    **self.meta_periodos["zero_field_row"],
                }
                self.av.data.append(data_row)
            data_row['meta'] = row['meta_estoque']
            data_row['data'] = row['data']
            self.inclui_referencias_adicionadas(data_row)

    def add_link_modelo(self):
        for row in self.av.data:
            row['modelo|TARGET'] = '_blank'
            row['modelo|LINK'] = reverse(
                'comercial:define_meta__get',
                args=[row['modelo']],
            )

    def av_data_sorted(self):
        return sorted(
            self.av.data,
            key=lambda k: (
                0 if k['meta'] == ' ' else -k['meta'],
                -k['ponderada'],
                int(k['modelo']),
            )
        )

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.meta_periodos = get_meta_periodos()
        
        self.get_av()

        self.insere_metas()

        self.calc_ponderada()

        self.add_link_modelo()
        data = self.av_data_sorted()

        self.context.update({
            'headers': [
                'Modelo', 'Meta de estoque', 'Data da meta', 'Venda ponderada',
                *self.meta_periodos['headers']
            ],
            'fields': [
                'modelo', 'meta', 'data', 'ponderada',
                *self.meta_periodos['col_fields']
            ],
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: center;',
                4: 'text-align: right;',
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
            },
        })
