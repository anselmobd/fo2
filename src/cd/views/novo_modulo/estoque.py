import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

from cd.forms.novo_modulo.estoque import NovoEstoqueForm
from cd.queries.novo_modulo import refs_em_palets


class NovoEstoque(O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = NovoEstoqueForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/estoque.html'
        self.title_name = 'Estoque'

        self.lotes_por_pagina = 20

        self.table_defs = TableDefs(
            {
                'palete rota modelo cor lote': [],
                'palete_dt': ['Data/Hora'],
                'endereco': ['Endereço'],
                'ref': ['Ref.'],
                'tam': ['Tam.'],
                'op': ['OP'],
                'qtd_prog qtd_lote': ['Tam.Lote', 'r'],
                'qtd_dbaixa': ['Qtd.Est.', 'r'],
                'estagio': ['Estágio', 'c'],
                'solicitacoes': ['Solicitações', 'c'],
                'sol_fin': ['Solicit.Fin.', 'c'],
                'sol': ['Solicitação'],
                'qtd_emp': ['Qtd.Empen.', 'r'],
                'qtd_sol': [
                    ('Qtd.Solic.<span id="select_sum"></span> ',),
                    'r'
                ],
                'tot_emp': ['Tot.Empen.', 'r'],
                'qtd_disp': ['Qtd.Disp.', 'r'],
                'qtd_fin': ['Qtd.Fin.', 'r'],
                'sit': ['Situação'],
                'ped_dest': ['Ped.Destino'],
                'ref_dest': ['Ref.Destino'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def get_lotes_como_disponibilidade(self):
        if self.situacao_empenho == 'esf':
            fields = 'detalhe+fin'
        else:
            fields = 'detalhe'
        dados = refs_em_palets.query(
            self.cursor,
            fields=fields,
            modelo=self.modelo,
            ref=self.referencia,
            cor=self.cor,
            tam=self.tam,
            colecao=self.colecao,
            op=self.op,
            lote=self.lote,
            endereco=self.endereco,
            tipo_prod=self.tipo_prod,
            selecao_ops=self.selecao_ops,
            selecao_lotes=self.selecao_lotes,
            situacao_empenho=self.situacao_empenho,
            paletizado=self.paletizado,
            qtd_empenhada=self.qtd_empenhada,
            qtd_solicitada=self.qtd_solicitada,
            solicitacoes=self.solicitacoes,
            modelos=self.modelos,
        )
        for row in dados:
            if row['est_sol'] and row['estagio'] != row['est_sol']:
                row['solicitacoes'] = '-'
                row['qtd_emp'] = 0
                row['qtd_sol'] = 0
            row['qtd_dbaixa'] = row['qtd']
            row['tot_emp'] = row['qtd_emp'] + row['qtd_sol']
            row['qtd_disp'] = row['qtd_dbaixa'] - row['tot_emp']
        return dados


    def mount_lotes_em_estoque(self):

        if self.order:
            if self.order in ['elpp', 'eld']:
                self.lotes.sort(key=operator.itemgetter('endereco', 'op', 'lote'))
            elif self.order == 'mod':
                self.lotes.sort(key=operator.itemgetter(
                    'modelo', 'ref', 'ordem_tam', 'cor', 'endereco', 'op', 'lote'))
            elif self.order == 'emp':
                self.lotes.sort(key=operator.itemgetter(
                    'modelo', 'ref', 'ordem_tam', 'cor', 'qtd_sol', 'endereco', 'op', 'lote'))

        for row in self.lotes:
            row['qtd_sol|CLASS'] = 'select_value'
            row['lote|CLASS'] = 'select_mark'
            row['endereco|CLASS'] = 'select_mark'
            row['solicitacoes|CLASS'] = 'select_mark'
        len_lotes = len(self.lotes)
        sum_fields = ['qtd_dbaixa', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp']
        if self.situacao_empenho == 'esf':
            sum_fields.append('qtd_fin')
        totalize_data(
            self.lotes,
            {
                'sum': sum_fields,
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        totalizador_lotes = self.lotes.pop()

        if self.order == 'elpp' and self.usa_paginador == 'n':
            field = 'endereco'
            old_value = None
            new_lotes = []
            for row in self.lotes:
                if row[field] != old_value:
                    new_row = {}
                    for key in row:
                        new_row[key] = row[key] if key == field else ''
                    new_row['|STYLE'] = 'font-weight: bold;'
                    if old_value is not None:
                        new_row['|CLASS'] = 'pagebreak'
                    new_lotes.append(new_row)
                new_lotes.append(row)
                old_value = row[field]
            self.lotes = new_lotes

        self.lotes = paginator_basic(self.lotes, self.lotes_por_pagina, self.page)

        for row in self.lotes.object_list:
            if row['qtd_disp'] and row['qtd_disp'] < 0:
                row['qtd_disp|STYLE'] = 'color: red;'

        self.lotes.object_list.append(totalizador_lotes)

        fields = [
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
            'solicitacoes', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp',
        ]
        if self.palete_dt == 's':
            fields.insert(1, 'palete_dt')
        if self.situacao_empenho == 'esf':
            fields.append('sol_fin')
            fields.append('qtd_fin')
        self.context.update(self.table_defs.hfs_dict(*fields))
        self.context.update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes,
            'len_lotes': len_lotes,
        })

    def mount_estoque(self):
        self.lotes = self.get_lotes_como_disponibilidade()

        if len(self.lotes) > 0:
            self.mount_lotes_em_estoque()

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

        if self.usa_paginador == 'n':
            self.lotes_por_pagina = 999999

        self.oc = self.lote[4:] if self.lote else None

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.filter_inputs()

        self.mount_estoque()
