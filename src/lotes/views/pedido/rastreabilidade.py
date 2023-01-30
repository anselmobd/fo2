from pprint import pprint

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2
from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.dictlist.row_field import (
    fld_a_blank,
    fld_date_dash,
    fld_default,
    fld_str,
    fld_str_dash,
)
from utils.table_defs import TableDefsHpSD
from utils.views.summarize import brif

from insumo.queries import rolo_inform

from lotes.queries.corte import (
    nfs_de_forn,
)
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

    def create_table(self, data, titulo=None, dados_titulo=None, titulo_h=3, vazio=None):
        return {
            'titulo': titulo,
            'dados_titulo': dados_titulo,
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
            fld_a_blank(row, 'pedido_venda', 'producao:pedido__get', post_process=fld_str)
            fld_default(row, 'fantasia')
            fld_default(row, 'pedido_cliente')
            fld_date_dash(row, 'dt_emissao')
            fld_date_dash(row, 'dt_embarque')
            fld_default(row, 'observacao')

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
            fld_a_blank(row, 'op_princ', 'producao:op__get', default='-')
            fld_a_blank(row, 'ref', 'produto:ref__get')
            fld_str_dash(row, 'op')
            fld_date_dash(row, 'dt_canc')
            fld_date_dash(row, 'dt_corte')
            fld_date_dash(row, 'dt_emit')
            fld_default(row, 'obs')
            fld_default(row, 'obs2')

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

    def get_rolos(self, op):
        return rolo_inform.query(
            self.cursor, op=op)

    def prep_rolos(self):
        for row in self.rolos_nfs:
            fld_a_blank(
                row,
                'nf',
                'contabil:nf_recebida__get',
                '1',
                row['nf_num'],
                row['nf_ser'],
                row['cnpj9'],
                is_empty_also='-',
            )
            row['nf_envia'] = '-'
            row['empr'] = None
            dados_nfs = nfs_de_forn.query(
                self.cursor,
                empr='1',
                nf_num=row['nf_num'],
                nf_ser=row['nf_ser'],
                cnpj9=row['cnpj9'],
            )
            if dados_nfs:
                row['nf_envia'] = dados_nfs[0]['nf_envia']
                row['empr'] = dados_nfs[0]['empr']
                fld_a_blank(
                    row,
                    'nf_envia',
                    'contabil:nota_fiscal__get',
                    row['empr'],
                    row['nf_envia'],
                    post_process=fld_str,
                    )

    def info_rolos(self, op):
        self.rolos = self.get_rolos(op)
        self.rolos_nfs = brif(
            self.rolos,
            [
                'forn',
                'cnpj9',
                'forn_cnpj',
                'nf',
                'nf_num',
                'nf_ser',
                'item',
            ],
            sum=[
                'peso',
            ]
        )
        self.prep_rolos()

    def table_rolos(self):
        bloco = self.create_table(
            self.rolos_nfs,
            dados_titulo='Rolos',
            titulo_h=4,
        )
        TableDefsHpSD({
            'forn': ["Fornecedor"],
            'forn_cnpj': ['CNPJ'],
            'nf': ["NF"],
            'item': ['Item'],
            'brif_count': ["Qtd. rolos"],
            'peso': ["Peso bruto"],
            'nf_envia': ["NF de envio"],
        }).hfs_dict_context(bloco)
        return bloco

    def info_ops(self):
        self.dados_ops = self.get_dados_ops()
        self.prep_rows_ops()
        ops = []
        for row in self.dados_ops:
            self.info_rolos(row['op'])
            ops.append({
                'op': row['op'],
                'tipo_ref': row['tipo_ref'],
                'ref': self.table_op_ref([row]),
                'info': self.table_op_info([row]),
                'obs': self.table_op_obs([row]),
                'rolos': self.table_rolos(),
            })
        self.context['ops'] = ops

    def get_dados_pedfm(self):

        def add_dados(dados_add):
            dados.extend([
                row
                for row in dados_add
                if row['ped'] not in pedidos_set
            ])
            pedidos_set.update([
                row['ped']
                for row in dados_add
            ])

        fantasia = self.dados_pedido[0]['fantasia']
        pedido_cliente = self.dados_pedido[0]['pedido_cliente']
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
        add_dados(dados_ops)

        dados_ped_cli = pedidos_filial_na_data(
            self.cursor, data_de=dt_emit, fantasia=fantasia,
            pedido_cliente=pedido_cliente)
        add_dados(dados_ped_cli)

        return dados

    def prep_rows_pedfm(self):
        for row in self.dados_filial_ped:
            fld_a_blank(row, 'ped', 'producao:pedido__get', post_process=fld_str)
            fld_date_dash(row, 'data')
            fld_str_dash(row, 'obs')
            fld_a_blank(
                row,
                'nf',
                'contabil:nota_fiscal__get',
                row['nf_empresa'],
                row['nf'],
                default='-',
                post_process=fld_str,
            )
            fld_str_dash(row, 'situacao_descr')

    def table_pedfm(self):
        bloco = self.create_table(
            self.dados_filial_ped,
            titulo='Pedido FM (auxiliar para faturamento Filial-Matriz)',
            vazio='Nenhum pedido gerado'
        )
        TableDefsHpSD({
            'ped': ["Pedido"],
            'data': ["Data pedido", 'c'],
            'obs': ["Observação"],
            'nf': ["NF"],
            'nf_data': ["Data NF"],
            'situacao_descr': ["Situação"],
        }).hfs_dict_context(bloco)
        return bloco

    def info_pedfm(self):
        self.dados_filial_ped = self.get_dados_pedfm()
        self.prep_rows_pedfm()
        self.context.update({
            'pedfm': self.table_pedfm(),
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

        if self.dados_ops:
            self.info_pedfm()
