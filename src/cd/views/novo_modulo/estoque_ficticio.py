import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

from cd.forms.novo_estoque_ficticio import NovoEstoqueFicticioForm
from cd.queries.novo_modulo import estoque_ficticio


class NovoEstoqueFicticio(O2BaseGetPostView):

    def __init__(self):
        super(NovoEstoqueFicticio, self).__init__()
        self.Form_class = NovoEstoqueFicticioForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque_ficticio.html'
        self.title_name = 'Estoque (Fictício)'

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
                'qtd_disp': ['Qtd.Disp.', 'r'],
                'sit': ['Situação'],
                'ped_dest': ['Ped.Destino'],
                'ref_dest': ['Ref.Destino'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def get_lotes_em_estoque(self):
        dados = estoque_ficticio.query(self.cursor)
        return dados

    def mount_lotes_em_estoque(self):
        totalize_data(
            self.lotes,
            {
                'sum': ['qtd_dbaixa', 'qtd_emp', 'qtd_sol'],
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

        # for row in self.lotes.object_list:
        #     if row['qtd_disp'] < 0:
        #         row['qtd_disp|STYLE'] = 'color: red;'

        self.lotes.object_list.append(totalizador_lotes)

        self.context.update(self.table_defs.hfs_dict(
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
            'solicitacoes', 'qtd_emp', 'qtd_sol',
        ))
        self.context.update({
            'safe': [
                'op',
            ],
            'data': self.lotes,
        })

    def mount_estoque(self):
        self.lotes = self.get_lotes_em_estoque()

        if len(self.lotes) > 0:
            self.mount_lotes_em_estoque()

    def filter_inputs(self):
        self.referencia = None if self.referencia == '' else self.referencia
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam

        # if self.usa_paginador == 'n':
        #     self.lotes_por_pagina = 99999

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.filter_inputs()

        self.mount_estoque()
