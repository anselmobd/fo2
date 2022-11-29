from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2
from base.views import O2BaseGetPostView
from utils.functions.models.dictlist import (
    row_field_date,
    row_field_empty,
)
from utils.table_defs import TableDefsHpSD

from lotes.queries.pedido.rastreabilidade import rastreabilidade_query
from lotes.queries.pedido.ped_inform import ped_inform_lower


class RastreabilidadeView(O2BaseGetPostView):

    def __init__(self):
        super(RastreabilidadeView, self).__init__()
        self.Form_class = Forms2().Pedido
        self.template_name = 'lotes/rastreabilidade.html'
        self.title_name = 'Rastreabilidade'
        self.form_class_has_initial = True
        self.cleaned_data2self = True

    def get_pedidos(self):
        return ped_inform_lower(
            self.cursor,
            pedido=self.pedido,
        )

    def config_bloco(self, data):
        return {
            # 'titulo': 'Pedidos',
            'data': data,
            'vazio': "Sem pedidos",
        }

    def prep_rows(self, bloco):
        for row in bloco['data']:
            # row['pedido_venda|TARGET'] = '_blank'
            # row['pedido_venda|A'] = reverse(
            #     'producao:pedido__get',
            #     args=[row['pedido_venda']],
            # )
            row_field_empty(row, 'fantasia')
            row_field_empty(row, 'pedido_cliente')
            row_field_date(row, 'dt_emissao')
            row_field_date(row, 'dt_embarque')
            row_field_empty(row, 'observacao')

    def define_hfs(self, bloco):
        TableDefsHpSD({
            'deposito': ["Depósito"],
            'dt_emissao': ["Emissão"],
            'dt_embarque': ["Embarque"],
            'cliente': ["cliente"],
            'fantasia': ["Fantasia"],
            'pedido_cliente': ["Pedido Cliente"],
            'observacao': ["Observação"],
        }).hfs_dict(context=bloco)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.context['pedido'] = self.pedido

        dados_pedidos = self.get_pedidos()
        bloco_pedidos = self.config_bloco(dados_pedidos)

        if dados_pedidos:
            self.prep_rows(bloco_pedidos)
            self.define_hfs(bloco_pedidos)

        self.context['pedidos'] = bloco_pedidos
