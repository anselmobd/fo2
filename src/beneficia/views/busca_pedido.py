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

    def config_bloco(self, data):
        return {
            'titulo': 'Pedidos',
            'data': data,
            'vazio': "Sem pedidos",
        }

    def prep_rows(self, bloco):
        for row in bloco['data']:
            row['pedido|TARGET'] = '_blank'
            row['pedido|A'] = reverse(
                'producao:pedido__get',
                args=[row['pedido']],
            )
            row['dt_emissao'] = (
                row['dt_emissao'].date() if row['dt_emissao'] else '-')
            if row['nf']:
                row['nf|TARGET'] = '_blank'
                row['nf|A'] = reverse(
                    'contabil:nota_fiscal__get',
                    args=[2, row['nf']]
                )
            else:
                row['nf'] = '-'
            if not row['obs']:
                row['obs'] = '-'

    def define_hfs(self, bloco):
        TableDefsHpSD({
            'pedido': ["Pedido"],
            'dt_emissao': ["Emissão"],
            'nf': ["NF"],
            'obs': ["Observação"],
        }).hfs_dict(context=bloco)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados_pedidos = self.get_pedidos()
        bloco_pedidos = self.config_bloco(dados_pedidos)

        if dados_pedidos:
            self.prep_rows(bloco_pedidos)
            self.define_hfs(bloco_pedidos)

        self.context['pedidos'] = bloco_pedidos
