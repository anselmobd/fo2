from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.functions.functions import untuple_keys_concat
from utils.table_defs import TableDefs
from utils.views import totalize_data

import cd.forms
from cd.queries.novo_modulo.lotes_em_estoque import LotesEmEstoque
from cd.queries.mount.records import Records


class NovoEstoque(O2BaseGetPostView):

    def __init__(self):
        super(NovoEstoque, self).__init__()
        self.Form_class = cd.forms.NovoEstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'
        self.lotes_por_pagina = 20

    def get_lotes_em_estoque(self):
        lotes_em_estoque = LotesEmEstoque(
            self.cursor,
            tipo='iq',
            lote=self.lote,
            ref=self.referencia,
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            endereco=self.endereco,
            op=self.op,
            fields_tuple=(
                'tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
                'palete',
                'endereco',
                'rota',
                'estagio',
                'solicitacoes',
            ),
        )
        return lotes_em_estoque.dados()

    def mount_lotes_em_estoque(self):
        totalize_data(
            self.lotes,
            {
                'sum': ['qtd_dbaixa'],
                'descr': {'lote': 'Total geral:'}
            }
        )
        totalizador_lotes = self.lotes[-1]
        del(self.lotes[-1])

        self.lotes = paginator_basic(self.lotes, self.lotes_por_pagina, self.page)
        self.lotes.object_list.append(totalizador_lotes)

        self.table_defs = TableDefs(
            {
                'palete': [],
                'endereco': ['Endereço'],
                'rota': [],
                'modelo': [],
                'ref': ['Ref.'],
                'tam': ['Tam.'],
                'cor': [],
                'op': ['OP'],
                'lote': [],
                'qtd_prog': ['Qtd.Original', 'r'],
                'qtd_dbaixa': ['Qtd.', 'r'],
                'estagio': ['Estágio', 'c'],
                'solicitacoes': ['Solicitações'],
            },
            ['header', '+style'],
            style = {
                'r': 'text-align: right;',
                'c': 'text-align: center;',
            }
        )

        headers, fields, style = self.table_defs.hfs()
        self.context.update({
            'headers': headers,
            'fields': fields,
            'safe': [
                'op',
            ],
            'style': style,
            'data': self.lotes,
        })

    def mount_estoque(self):
        self.lotes = self.get_lotes_em_estoque()

        if len(self.lotes) > 0:
            self.mount_lotes_em_estoque()

    def get_records_data(self):
        records = Records(
            self.cursor,
            table='lp',
            filter={
                'lp.lote': self.lote,
                'lp.op': self.op,
                'op.ref': self.referencia,
                'l_ref.cor': self.cor,
                'l_ref.tam': self.tam,
            },
            select=(
                'lp.palete',
                'op.ref',
                'l_ref.cor',
                'l_ref.tam',
                'lp.op',
                'lp.lote',
                'l_ref.qtd_lote',
                'sl.sol',
                'sl.qtd qtd_sol',
                'sl.sit',
                'sl.ped_dest',
                'sl.ref_dest',
            )
        )
        return records.data()[:100]

    def mount_records_data(self):
        totalize_data(
            self.rec_data,
            {
                'sum': ['qtd_sol'],
                'descr': {'sol': 'Total:'}
            }
        )

        colunas = (
            'palete',
            'ref',
            'cor',
            'tam',
            'op',
            'lote',
            'qtd_lote',
            'sol',
            'qtd_sol',
            'sit',
            'ped_dest',
            'ref_dest',
        )
        self.context.update({
            'r_headers': colunas,
            'r_fields': colunas,
            'r_data': self.rec_data,
        })

    def mount_estoque_test(self):
        if any([
            self.lote,
            self.op,
            self.referencia,
            self.cor,
            self.tam,
        ]):

            self.rec_data = self.get_records_data()

            if len(self.rec_data) > 0:
                self.mount_records_data()

        # records = Records(
        #     self.cursor,
        # )
        # pprint(records.data()[:10])

    def filter_inputs(self):
        self.lote = None if self.lote == '' else self.lote
        self.op = None if self.op == '' else self.op
        self.referencia = None if self.referencia == '' else self.referencia
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam
        self.modelo = None if self.modelo == '' else int(self.modelo)
        self.endereco = None if self.endereco == '' else self.endereco

        # if self.usa_paginador == 'n':
        #     self.lotes_por_pagina = 99999

        self.oc = self.lote[4:] if self.lote else None

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.filter_inputs()

        self.mount_estoque()

        self.mount_estoque_test()
