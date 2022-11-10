import re
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions.strings import min_max_string
from utils.functions.date import dmy_or_empty
from utils.table_defs import TableDefsHpSD
from utils.views import totalize_data

from beneficia.forms.busca_pedido import Form as BuscaPedidoForm
from beneficia.queries.busca_pedido import query as busca_pedido_query


class BuscaPedido(O2BaseGetPostView):

    def __init__(self):
        super(BuscaPedido, self).__init__()
        self.Form_class = BuscaPedidoForm
        self.template_name = 'beneficia/busca_pedido.html'
        self.title_name = 'Busca Pedido'
        self.form_class_has_initial = True
        self.cleaned_data2self = True

    def get_pedidos(self):
        return busca_pedido_query(
            self.cursor,
            emissao_de=self.data_de,
            emissao_ate=self.data_ate,
        )

    def mount_pedidos(self):
        return {
            'titulo': 'Pedidos',
            'data': self.get_pedidos(),
            'vazio': "Sem pedidos",
        }

    def prepara_campos(self, dados):
        for row in dados['data']:
            row['pedido|TARGET'] = '_blank'
            row['pedido|LINK'] = reverse(
                'producao:pedido__get',
                args=[row['pedido']],
            )

    def define_hfs(self, dados):
        TableDefsHpSD({
            'pedido': ["Pedido"],
            'dt_emissao': ["Emissão"],
        }).hfs_dict(context=dados)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        pedidos = self.mount_pedidos()

        if pedidos['data']:
            self.prepara_campos(pedidos)
            self.define_hfs(pedidos)

        self.context['pedidos'] = pedidos
