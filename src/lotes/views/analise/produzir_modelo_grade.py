from pprint import pprint

from django.db import connections
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetPostView, O2BaseGetView
from geral.functions import config_get_value
from utils.views import totalize_data

import comercial.models

import lotes.forms


class ProduzirModeloGrade(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ProduzirModeloGrade, self).__init__(*args, **kwargs)
        # self.Form_class = lotes.forms.ProduzirModeloGradeForm
        self.template_name = 'lotes/analise/produzir_modelo_grade.html'
        self.title_name = 'Aproduzir - Por modelo - Totais com grade'

    def mount_context(self):
        cursor = connections['so'].cursor()

        data = []

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.exclude(venda_mensal=0)
        metas = metas.values()

        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                }
                data.append(data_row)
            data_row['meta_giro'] = row['meta_giro']
            data_row['meta_estoque'] = row['meta_estoque']
            data_row['meta'] = row['meta_giro'] + row['meta_estoque']
            data_row['total_op'] = 0
            data_row['total_op|CLASS'] = 'total_op-{}'.format(row['modelo'])
            data_row['total_est'] = 0
            data_row['total_est|CLASS'] = 'total_est-{}'.format(row['modelo'])
            data_row['total_ped'] = 0
            data_row['total_ped|CLASS'] = 'total_ped-{}'.format(row['modelo'])
            data_row['op_menos_ped'] = 0
            data_row['op_menos_ped|CLASS'] = 'op_menos_ped-{}'.format(
                row['modelo'])
            data_row['a_produzir'] = data_row['meta']
            data_row['a_produzir|CLASS'] = 'a_produzir-{}'.format(
                row['modelo'])
            data_row['excesso'] = 0
            data_row['excesso|CLASS'] = 'excesso-{}'.format(
                row['modelo'])

        data = sorted(data, key=lambda i: -i['meta'])

        totalize_data(data, {
            'sum': ['meta_giro', 'meta_estoque', 'meta',
                    'total_op', 'total_est', 'total_ped',
                    'op_menos_ped', 'a_produzir', 'excesso'],
            'count': [],
            'descr': {'modelo': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'class_suffix': '__total',
        })

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.context.update({
            'dias_alem_lead': dias_alem_lead,
            'headers': ['Modelo', 'Meta de estoque', 'Meta de giro (lead)',
                        'Total das metas(A)', 'Total das OPs',
                        'Total nos depósitos', 'Carteira de pedidos',
                        'OPs+Depósitos–Pedidos(B)', 'A produzir(A-B)[+]',
                        'Excesso(A-B)[-]'],
            'fields': ['modelo', 'meta_estoque', 'meta_giro',
                       'meta', 'total_op',
                       'total_est', 'total_ped',
                       'op_menos_ped', 'a_produzir',
                       'excesso'],
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
                10: 'text-align: right;',
            },
        })
