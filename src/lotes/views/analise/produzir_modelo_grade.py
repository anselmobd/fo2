from pprint import pprint

from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.views import totalize_data
from utils.table_defs import TableDefs

import comercial.models

from lotes.queries.analise.produzir_grade_empenho import mount_produzir_grade_empenho


class ProduzirModeloGrade(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ProduzirModeloGrade, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/analise/produzir_modelo_grade.html'
        self.title_name = 'A produzir - Por modelo - Totais com grade'

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

    def get_total(self, dados, grade):
        if grade in dados:
            for row in dados[grade]['data']:
                if row['cor'] == 'Total':
                    return row['total']
        else:
            return 0

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = []

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

        for row in metas:
            modelo = row['modelo']
            data_row = {}
            data.append(data_row)
            dados_produzir = mount_produzir_grade_empenho(cursor, modelo)
            data_row['modelo'] = modelo
            data_row['modelo|CLASS'] = 'modelo'
            data_row['meta_estoque'] = self.get_total(dados_produzir, 'gme')
            data_row['meta_giro'] = self.get_total(dados_produzir, 'gmg')
            data_row['meta'] = self.get_total(dados_produzir, 'gm')
            data_row['inventario'] = self.get_total(dados_produzir, 'ginv')
            data_row['inventario|CLASS'] = f'inventario-{modelo}'
            data_row['op_andamento'] = self.get_total(dados_produzir, 'gopa_ncd')
            data_row['op_andamento|CLASS'] = f'op_andamento-{modelo}'
            data_row['total_op'] = self.get_total(dados_produzir, 'gopa')
            data_row['total_op|CLASS'] = f'total_op-{modelo}'
            data_row['empenho'] = self.get_total(dados_produzir, 'gsol')
            data_row['empenho|CLASS'] = f'empenho-{modelo}'
            data_row['pedido'] = self.get_total(dados_produzir, 'gped')
            data_row['pedido|CLASS'] = f'pedido-{modelo}'
            data_row['livres'] = self.get_total(dados_produzir, 'gopp')
            data_row['livres|CLASS'] = f'livres-{modelo}'
            data_row['excesso'] = self.get_total(dados_produzir, 'gex')
            data_row['excesso|CLASS'] = f'excesso-{modelo}'
            data_row['a_produzir'] = self.get_total(dados_produzir, 'gap')
            data_row['a_produzir|CLASS'] = f'a_produzir-{modelo}'
            data_row['a_produzir_tam'] = self.get_total(dados_produzir, 'glm')
            data_row['a_produzir_tam|CLASS'] = f'a_produzir_tam-{modelo}'
            data_row['a_produzir_cor'] = self.get_total(dados_produzir, 'glc')
            data_row['a_produzir_cor|CLASS'] = f'a_produzir_cor-{modelo}'

        data = sorted(data, key=lambda i: -i['meta'])

        totalize_data(data, {
            'sum': self.val_fields,
            'count': [],
            'descr': {'modelo': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'class_suffix': '__total',
        })

        self.context.update(
            self.table_defs.hfs_dict()
        )
        self.context.update({
            'data': data,
        })
