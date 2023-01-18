from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2
from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.dictlist import (
    row_field_date,
    row_field_empty,
    row_field_str,
)
from utils.table_defs import TableDefsHpSD

from lotes.queries.pedido.pedido_filial import (
    pedidos_filial_na_data,
)
from lotes.queries.rastreabilidade import (
    pedido_op,
)
from lotes.queries.pedido.ped_inform import ped_inform


class RastreabilidadeView(O2BaseGetPostView):

    def __init__(self):
        super(RastreabilidadeView, self).__init__()
        self.Form_class = Forms2().Pedido
        self.template_name = 'lotes/rastreabilidade.html'
        self.title_name = 'Rastreabilidade'
        self.cleaned_data2self = True
        self.get_args = ['pedido']

    def create_table(self, data, titulo=None, titulo_h=4, vazio=None):
        return {
            'titulo': titulo,
            'titulo_h': titulo_h,
            'data': data,
            'vazio': vazio,
        }

    def get_dados_pedido(self):
        return ped_inform(
            self.cursor,
            pedido=self.pedido,
            empresa=None,
            lower=True,
        )

    def prep_rows_pedido(self):
        for row in self.dados_pedido:
            row['pedido_venda|TARGET'] = '_blank'
            row['pedido_venda|A'] = reverse(
                'producao:pedido__get',
                args=[row['pedido_venda']],
            )
            row_field_empty(row, 'fantasia')
            row_field_empty(row, 'pedido_cliente')
            row_field_date(row, 'dt_emissao')
            row_field_date(row, 'dt_embarque')
            row_field_empty(row, 'observacao')

    def table_ped_cliente(self):
        bloco = self.create_table(self.dados_pedido)
        TableDefsHpSD({
            'empresa': ["Empresa"],
            'pedido_venda': ["Pedido"],
            'deposito': ["Depósito"],
            'fantasia': ["Fantasia"],
            'cliente': ["Cliente"],
            'pedido_cliente': ["Pedido Cliente"],
        }).hfs_dict_context(bloco)
        return bloco

    def table_ped_status(self):
        bloco = self.create_table(self.dados_pedido)
        TableDefsHpSD({
            'dt_embarque': ["Embarque"],
            'dt_emissao': ["Emissão"],
            'status_pedido': ["Status pedido"],
            'cancelamento_descr': ["Cancelamento"],
            'situacao_venda': ["Situação venda"],
        }).hfs_dict_context(bloco)
        return bloco

    def table_ped_obs(self):
        bloco = self.create_table(self.dados_pedido)
        TableDefsHpSD({
            'observacao': ["Observação"],
        }).hfs_dict_context(bloco)
        return bloco

    def info_pedido(self):
        self.prep_rows_pedido()
        self.context.update({
            'cliente': self.table_ped_cliente(),
            'status': self.table_ped_status(),
            'obs': self.table_ped_obs(),
        })

    def get_dados_ops(self):
        return pedido_op.query(
            self.cursor,
            pedido=self.pedido,
        )

    def prep_rows_ops(self):
        for row in self.dados_ops:
            if row['op_princ']:
                row['op_princ|TARGET'] = '_blank'
                row['op_princ|A'] = reverse(
                    'producao:op__get',
                    args=[row['op_princ']],
                )
            row['ref|TARGET'] = '_blank'
            row['ref|A'] = reverse(
                'produto:ref__get',
                args=[row['ref']],
            )
            row_field_str(row, 'op')
            row_field_date(row, 'dt_canc')
            row_field_date(row, 'dt_corte')
            row_field_date(row, 'dt_emit')
            row_field_str(row, 'op_princ')
            row_field_empty(row, 'obs')
            row_field_empty(row, 'obs2')

    def table_op_ref(self, dados):
        bloco = self.create_table(dados)
        TableDefsHpSD({
            'dt_emit': ["Data emissão"],
            'ref': ["Referência"],
            'ref_descr': ["Ref. Descr."],
            'colecao': ["Coleção"],
            'qtd': ["Quant."],
        }).hfs_dict_context(bloco)
        return bloco

    def table_op_info(self, dados):
        bloco = self.create_table(dados)
        TableDefsHpSD({
            'dep': ["Depósito"],
            'alt': ["Alternativa"],
            'tipo_progr_descr': ["Tipo programação"],
            'dt_corte': ["Data corte"],
            'op_princ': ["OP mãe"],
            'canc': ["Cancelamento"],
            'dt_canc': ["Data Canc."],
        }).hfs_dict_context(bloco)
        return bloco

    def table_op_obs(self, dados):
        bloco = self.create_table(dados)
        TableDefsHpSD({
            'obs': ["Observação"],
            'obs2': ["Observação 2"],
        }).hfs_dict_context(bloco)
        return bloco

    def info_ops(self):
        self.dados_ops = self.get_dados_ops()
        self.prep_rows_ops()
        ops = []
        for row in self.dados_ops:
            ops.append({
                'op': row['op'],
                'tipo_ref': row['tipo_ref'],
                'ref': self.table_op_ref([row]),
                'info': self.table_op_info([row]),
                'obs': self.table_op_obs([row]),
            })
        self.context['ops'] = ops

    def get_dados_filial_pedido(self):
        fantasia = self.dados_pedido[0]['fantasia']
        ops = [
            op['op']
            for op in self.dados_ops
        ]
        dt_emit = min([
            op['dt_emit']
            for op in self.dados_ops
        ])

        pedidos_set = set()
        dados = []

        dados_ops = pedidos_filial_na_data(
            self.cursor, data_de=dt_emit, fantasia=fantasia, op=ops)
        dados.extend([
            row
            for row in dados_ops
            if row['ped'] not in pedidos_set
        ])
        pedidos_set.update([
            row['ped']
            for row in dados_ops
        ])

        return dados

    def prep_rows_filial_pedido(self):
        for row in self.dados_filial_ped:
            row_field_str(row, 'ped')
            row_field_date(row, 'data')
            row_field_str(row, 'nf')

    def table_filial_pedido(self):
        bloco = self.create_table(
            self.dados_filial_ped,
            titulo='Pedidos auxiliares para faturamento Filial-Matriz',
        )
        TableDefsHpSD({
            'ped': ["Pedido"],
            'data': ["Data pedido", 'c'],
            'obs': ["Observação"],
            'nf': ["NF"],
        }).hfs_dict_context(bloco)
        return bloco

    def info_filial_pedido(self):
        self.dados_filial_ped = self.get_dados_filial_pedido()
        self.prep_rows_filial_pedido()
        self.context.update({
            'filial_pedido': self.table_filial_pedido(),
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.context['pedido'] = self.pedido

        self.dados_pedido = self.get_dados_pedido()
        if not self.dados_pedido:
            self.context['mensagem'] = "Pedido não encontrado"
            return

        self.info_pedido()

        if self.dados_pedido[0]['codigo_empresa'] != 1:
            return

        self.info_ops()      

        self.info_filial_pedido()
