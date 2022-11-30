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

    def get_pedido(self):
        return ped_inform_lower(
            self.cursor,
            pedido=self.pedido,
        )

    def create_bloco(self, data, vazio=None):
        return {
            # 'titulo': 'Pedidos',
            'data': data,
            'vazio': vazio,
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

    def hfs_cliente(self, bloco):
        TableDefsHpSD({
            'deposito': ["Depósito"],
            'fantasia': ["Fantasia"],
            'cliente': ["Cliente"],
            'pedido_cliente': ["Pedido Cliente"],
        }).hfs_dict(context=bloco)

    def hfs_status(self, bloco):
        TableDefsHpSD({
            'dt_embarque': ["Embarque"],
            'dt_emissao': ["Emissão"],
            'status_pedido': ["Status pedido"],
            'cancelamento_descr': ["Cancelamento"],
            'situacao_venda': ["Situação venda"],
        }).hfs_dict(context=bloco)

    def hfs_obs(self, bloco):
        TableDefsHpSD({
            'observacao': ["Observação"],
        }).hfs_dict(context=bloco)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.context['pedido'] = self.pedido

        dados_pedido = self.get_pedido()
        bloco_cliente = self.create_bloco(
            dados_pedido,
            vazio="Pedido não encontrado",
        )
        self.context['cliente'] = bloco_cliente

        if not dados_pedido:
            return

        self.prep_rows(bloco_cliente)

        self.hfs_cliente(bloco_cliente)

        bloco_status = self.create_bloco(dados_pedido)
        self.hfs_status(bloco_status)
        self.context['status'] = bloco_status

        bloco_obs = self.create_bloco(dados_pedido)
        self.hfs_obs(bloco_obs)
        self.context['obs'] = bloco_obs
