import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

from cd.forms.novo_estoque import NovoEstoqueForm
from cd.queries.novo_modulo.lotes_em_estoque import LotesEmEstoque
from cd.queries.mount.records import Records
from cd.queries.novo_modulo import refs_em_palets


class NovoEstoque(O2BaseGetPostView):

    def __init__(self):
        super(NovoEstoque, self).__init__()
        self.Form_class = NovoEstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'

        self.lotes_por_pagina = 20

        self.table_defs = TableDefs(
            {
                'palete rota modelo cor lote': [],
                'endereco': ['Endereço'],
                'ref': ['Ref.'],
                'tam': ['Tam.'],
                'op': ['OP'],
                'qtd_prog qtd_lote': ['Tam.Lote', 'r'],
                'qtd_dbaixa': ['Qtd.Est.', 'r'],
                'estagio': ['Estágio', 'c'],
                'solicitacoes': ['Solicitações', 'c'],
                'sol': ['Solicitação'],
                'qtd_emp': ['Qtd.Empen.', 'r'],
                'qtd_sol': ['Qtd.Solic.', 'r'],
                'qtd_disp': ['Qtd.Disp.', 'r'],
                'sit': ['Situação'],
                'ped_dest': ['Ped.Destino'],
                'ref_dest': ['Ref.Destino'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def get_lotes_em_estoque(self):
        tipo = {
            'qq': 'iq',
            '63': 'i',
            'n63': 'in',
        }
        lotes_em_estoque = LotesEmEstoque(
            self.cursor,
            tipo=tipo[self.selecao_lotes],
            lote=self.lote,
            ref=self.referencia,
            cor=self.cor,
            tam=self.tam,
            colecao=self.colecao,
            modelo=self.modelo,
            endereco=self.endereco,
            op=self.op,
            fields_tuple=(
                'tam',
                'ordem_tam',
                'cor',
                'op',
                'lote',
                'qtd_prog',
                'qtd_dbaixa',
                'palete',
                'endereco',
                'rota',
                'estagio',
                'est_sol',
                'solicitacoes',
                'qtd_sol',
                'qtd_emp',
            ),
        )
        dados = lotes_em_estoque.dados()
        for row in dados:
            if row['estagio'] != row['est_sol']:
                row['solicitacoes'] = '-'
                row['qtd_emp'] = 0
                row['qtd_sol'] = 0
            row['qtd_disp'] = row['qtd_dbaixa'] - row['qtd_emp'] - row['qtd_sol']
        return dados

    def get_lotes_como_disponibilidade(self):
        dados = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            modelo=self.modelo,
            ref=self.referencia,
            cor=self.cor,
            tam=self.tam,
            colecao=self.colecao,
            op=self.op,
            lote=self.lote,
            endereco=self.endereco,
            selecao_lotes=self.selecao_lotes,
            paletezados=self.paletezados,
        )
        for row in dados:
            if row['estagio'] != row['est_sol']:
                row['solicitacoes'] = '-'
                row['qtd_emp'] = 0
                row['qtd_sol'] = 0
            row['qtd_dbaixa'] = row['qtd']
            row['qtd_disp'] = row['qtd_dbaixa'] - row['qtd_emp'] - row['qtd_sol']
        return dados


    def mount_lotes_em_estoque(self):

        if self.order:
            if self.order == 'el':
                self.lotes.sort(key=operator.itemgetter('endereco', 'lote', 'ref', 'ordem_tam', 'cor'))
            elif self.order == 'mod':
                self.lotes.sort(key=operator.itemgetter('modelo', 'ref', 'ordem_tam', 'cor', 'op', 'lote'))

        totalize_data(
            self.lotes,
            {
                'sum': ['qtd_dbaixa', 'qtd_emp', 'qtd_sol', 'qtd_disp'],
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        totalizador_lotes = self.lotes[-1]
        del(self.lotes[-1])

        self.lotes = paginator_basic(self.lotes, self.lotes_por_pagina, self.page)

        for row in self.lotes.object_list:
            if row['qtd_disp'] < 0:
                row['qtd_disp|STYLE'] = 'color: red;'

        self.lotes.object_list.append(totalizador_lotes)

        self.context.update(self.table_defs.hfs_dict(
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
            'solicitacoes', 'qtd_emp', 'qtd_sol', 'qtd_disp',
        ))
        self.context.update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes,
        })

    def mount_estoque(self):
        self.rotina = 'disponibilidade'
        if self.rotina == 'default':
            self.lotes = self.get_lotes_em_estoque()
        elif self.rotina == 'disponibilidade':
            self.lotes = self.get_lotes_como_disponibilidade()
        else:
            self.lotes = []

        if len(self.lotes) > 0:
            self.mount_lotes_em_estoque()

    def get_records_data(self):
        records = Records(
            self.cursor,
            filters={
                'lp.lote': self.lote,
                'lp.op': self.op,
                'op.ref': self.referencia,
                'l_ref.cor': self.cor,
                'l_ref.tam': self.tam,
            },
            fields=(
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
        dados = records.data()[:100]
        dados.sort(key=operator.itemgetter('lote', 'ref', 'tam', 'cor'))
        return dados

    def mount_records_data(self):
        totalize_data(
            self.rec_data,
            {
                'sum': ['qtd_sol'],
                'descr': {'sol': 'Total:'}
            }
        )
        self.context.update(self.table_defs.hfs_dict(
            'palete', 'ref', 'cor', 'tam',
            'op', 'lote', 'qtd_lote',
            'sol', 'qtd_sol', 'sit', 'ped_dest', 'ref_dest',
            sufixo='r_'
        ))
        self.context.update({
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
        self.order = None if self.order == '-' else self.order
        self.colecao = None if self.colecao == '' else self.colecao

        # if self.usa_paginador == 'n':
        #     self.lotes_por_pagina = 99999

        self.oc = self.lote[4:] if self.lote else None

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.filter_inputs()

        self.mount_estoque()

        # self.mount_estoque_test()
