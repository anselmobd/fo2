from pprint import pprint

from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from o2.views.base.get import O2BaseGetView
from utils.views import totalize_data
from utils.table_defs import TableDefs

import comercial.models


class ProduzirModeloGrade(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ProduzirModeloGrade, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/analise/produzir_modelo_grade.html'
        self.title_name = 'A produzir por modelo'

        self.table_defs = TableDefs(
            {
                'modelo': ["Modelo"],
                'meta_estoque': ["Meta de estoque", 'r'],
                'meta_giro': ["Meta de giro (lead)", 'r'],
                'meta': ["Total das metas(A)", 'r'],
                'inventario': ["Inventário/CD", 'r'],
                'op_andamento': ["OPs em andamento", 'r'],
                'total_op': ["Total em OPs", 'r'],
                'empenho': ["Empenhos", 'r'],
                'pedido': ["Carteira de pedidos", 'r'],
                'livres': ["OPs-Empenhos-Pedidos(B)", 'r'],
                'excesso': ["Excesso(A-B)[-]", 'r'],
                'a_produzir': ["A produzir(A-B)[+]", 'r'],
                'a_produzir_tam': ["A produzir lote tamanho", 'r'],
                'a_produzir_cor': ["A produzir lote cor", 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )
        self.val_fields = self.table_defs.definition.keys()
        self.val_fields = list(self.val_fields)
        self.val_fields.remove('modelo')

    def mount_context(self):
        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(
            antiga=False,
        )
        metas = metas.exclude(venda_mensal=0)
        metas = list(metas.values())

        data = []
        for meta in metas:
            modelo = meta['modelo']
            row = {}
            row['modelo'] = modelo
            row['modelo|CLASS'] = 'modelo'
            row['meta_estoque'] = meta['meta_estoque']
            row['meta_estoque|CLASS'] = f'meta_estoque-{modelo}'
            row['meta_giro'] = 0
            row['meta_giro|CLASS'] = f'meta_giro-{modelo}'
            row['meta'] = 0
            row['meta|CLASS'] = f'meta-{modelo}'
            row['inventario'] = 0
            row['inventario|CLASS'] = f'inventario-{modelo}'
            row['op_andamento'] = 0
            row['op_andamento|CLASS'] = f'op_andamento-{modelo}'
            row['total_op'] = 0
            row['total_op|CLASS'] = f'total_op-{modelo}'
            row['empenho'] = 0
            row['empenho|CLASS'] = f'empenho-{modelo}'
            row['pedido'] = 0
            row['pedido|CLASS'] = f'pedido-{modelo}'
            row['livres'] = 0
            row['livres|CLASS'] = f'livres-{modelo}'
            row['excesso'] = 0
            row['excesso|CLASS'] = f'excesso-{modelo}'
            row['a_produzir'] = 0
            row['a_produzir|CLASS'] = f'a_produzir-{modelo}'
            row['a_produzir_tam'] = 0
            row['a_produzir_tam|CLASS'] = f'a_produzir_tam-{modelo}'
            row['a_produzir_cor'] = 0
            row['a_produzir_cor|CLASS'] = f'a_produzir_cor-{modelo}'
            data.append(row)

        data = sorted(data, key=lambda i: -i['meta_estoque'])

        totalize_data(data, {
            'sum': self.val_fields,
            'count': [],
            'descr': {'modelo': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'class_suffix': '__total',
        })

        for row in data:
            row['meta_estoque'] = 0

        self.context.update(
            self.table_defs.hfs_dict()
        )
        self.context.update({
            'data': data,
        })
