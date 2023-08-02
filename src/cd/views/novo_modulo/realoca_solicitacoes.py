import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

import cd.forms
from cd.queries.novo_modulo import refs_em_palets
from cd.queries.novo_modulo.solicitacao import get_solicitacao


class RealocaSolicitacoes(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(RealocaSolicitacoes, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.RealocaSolicitacoesForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/realoca_solicitacoes.html'
        self.title_name = 'Realoca solicitações'

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
                'solicitacao': ['Solicitação', 'c'],
                'solicitacoes': ['Solicitações', 'c'],
                'sol_fin': ['Solicit.Fin.', 'c'],
                'sol': ['Solicitação'],
                'qtde': ['Qtd.', 'r'],
                'qtd_emp': ['Qtd.Empen.', 'r'],
                'qtd_sol': ['Qtd.Solic.', 'r'],
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

    def get_lotes(self):
        dados = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            endereco=self.endereco,
            tipo_prod='pagb',
            qtd_solicitada='nts',
            solicitacoes=self.solicitacoes,
        )
        for row in dados:
            row['qtd_dbaixa'] = row['qtd']
        return dados

    def mount_lotes(self):

        len_lotes = len(self.lotes)
        self.lotes.sort(key=operator.itemgetter('endereco', 'op', 'lote'))

        sum_fields = ['qtd_dbaixa']
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
        fields = [
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
        ]
        self.context['lotes'] = self.table_defs.hfs_dict(*fields)
        self.context['lotes'].update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes,
            'len': len_lotes,
        })

    def mount_lotes_disponiveis(self):
        self.lotes = self.get_lotes()
        if len(self.lotes) > 0:
            self.mount_lotes()

    def get_lotes_solis(self):
        dados = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            tipo_prod='pagb',
            qtd_solicitada='ps',
            solicitacoes=self.solicitacoes,
        )
        for row in dados:
            row['qtd_dbaixa'] = row['qtd']
            row['tot_emp'] = row['qtd_emp'] + row['qtd_sol']
            row['qtd_disp'] = row['qtd_dbaixa'] - row['tot_emp']
        return dados

    def mount_lotes_solis(self):

        len_lotes_solis = len(self.lotes_solis)
        self.lotes_solis.sort(key=operator.itemgetter('endereco', 'op', 'lote'))

        sum_fields = ['qtd_dbaixa', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp']
        totalize_data(
            self.lotes_solis,
            {
                'sum': sum_fields,
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        for row in self.lotes_solis:
            if row['qtd_disp'] < 0:
                row['qtd_disp|STYLE'] = 'color: red;'
        fields = [
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
            'solicitacoes', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp',
        ]
        self.context['lotes_solis'] = self.table_defs.hfs_dict(*fields)
        self.context['lotes_solis'].update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes_solis,
            'len': len_lotes_solis,
        })

    def mount_lotes_solicitados(self):
        self.lotes_solis = self.get_lotes_solis()
        self.lista_lotes = [
            row['lote']
            for row in self.lotes_solis
        ]
        if len(self.lotes_solis) > 0:
            self.mount_lotes_solis()

    def get_solis_tot(self, lotes):
        dados = get_solicitacao(
            self.cursor,
            solicitacao='!',
            lote=lotes,
            situacao=4,
        )
        return dados

    def mount_solis_tot(self):
        len_solis_tot = len(self.solis_tot)
        fields = [
            'lote', 'solicitacao', 'qtde'
        ]
        self.context['solis_tot'] = self.table_defs.hfs_dict(*fields)
        self.context['solis_tot'].update({
            'data': self.solis_tot,
            'len': len_solis_tot,
        })

    def mount_solis_totalizadas(self):
        self.solis_tot = self.get_solis_tot(self.lista_lotes)
        if len(self.solis_tot) > 0:
            self.mount_solis_tot()

    def filter_inputs(self):
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam
        self.modelo = None if self.modelo == '' else int(self.modelo)
        self.endereco = None if self.endereco == '' else self.endereco

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.filter_inputs()
        self.mount_lotes_solicitados()
        self.mount_solis_totalizadas()
        self.mount_lotes_disponiveis()
