import operator
from pprint import pprint, pformat

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions import coalesce
from utils.table_defs import TableDefs
from utils.views import totalize_data

import cd.forms
from cd.functions import oti_emp
from cd.queries.novo_modulo import refs_em_palets
from cd.queries.novo_modulo.solicitacao import get_solicitacao


class RealocaSolicitacoes(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(RealocaSolicitacoes, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.RealocaSolicitacoesForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/realoca_solicitacoes.html'
        self.title_name = 'Realoca empenhos'

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
                'solicitacao': ['Solicitação'],
                'pedido_destino': ['Pedido destino'],
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
        qtd_empenhada = 't' if self.qtd_empenhada == 'ce' else 'nte'
        lotes = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            endereco=self.endereco,
            tipo_prod='pagb',
            qtd_empenhada=qtd_empenhada,
            solicitacoes=self.solicitacoes,
        )
        lotes_a_trabalhar = []
        for row in lotes:
            row['qtd_dbaixa'] = row['qtd']
            if row['lote'] not in self.lotes_nao_trabalhar:
                lotes_a_trabalhar.append(row)
        lotes_a_trabalhar.sort(key=operator.itemgetter('endereco', 'op', 'lote'))
        return lotes_a_trabalhar

    def mount_lotes(self):
        len_lotes = len(self.lotes)
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

    def endereco_selecionado(self, end, selecao):
        if selecao:
            if len(selecao) == 6:
                return end == selecao
            elif '-' in selecao:
                end_de, end_ate = tuple(selecao.split('-'))
                return end >= end_de and end <= end_ate
            else:
                return end.startswith(selecao)
        return False

    def get_lotes_solis(self):
        empenhos = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            tipo_prod='pagb',
            qtd_empenhada=self.qtd_empenhada,
            solicitacoes=self.solicitacoes,
        )
        # só vai trabalhar nos lotes que não estão
        # - já nos endereços desejados; e
        # - com empenhos totais
        empenhos_a_trabalhar = []
        self.lotes_nao_trabalhar = []
        for row in empenhos:
            row['qtd_dbaixa'] = row['qtd']
            row['tot_emp'] = row['qtd_emp'] + row['qtd_sol']
            row['qtd_disp'] = row['qtd_dbaixa'] - row['tot_emp']
            if (
                (not self.endereco_selecionado(row['endereco'], self.endereco))
                or row['qtd_disp'] > 0
            ):
                empenhos_a_trabalhar.append(row)
            else:
                self.lotes_nao_trabalhar.append(row['lote'])
        empenhos_a_trabalhar.sort(key=operator.itemgetter('endereco', 'op', 'lote'))
        return empenhos_a_trabalhar

    def mount_lotes_solis(self):
        len_lotes_solis = len(self.lotes_solis)
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

    def get_solis_de_lotes(self):
        dados = get_solicitacao(
            self.cursor,
            solicitacao='!',
            lote=self.lista_lotes,
            situacao=(2, 3, 4),
        )
        return dados

    def get_solis(self):
        self.solis_de_lotes = self.get_solis_de_lotes()
        dados_dict = {}
        for row in self.solis_de_lotes:
            sol = row['solicitacao']
            ped = row['pedido_destino']
            key = (sol, ped)
            if key not in dados_dict:
                dados_dict[key] = 0
            dados_dict[key] += row['qtde']
        dados = [
            {
                'solicitacao': coalesce(key[0], 0),
                'pedido_destino': coalesce(key[1], 0),
                'qtde': qtde,
            }
            for key, qtde in dados_dict.items()
        ]
        dados.sort(key=operator.itemgetter('solicitacao', 'pedido_destino'))
        for row in dados:
            if row['solicitacao'] == 0:
                row['solicitacao'] = '#'
        return dados

    def mount_solis(self):
        len_solis = len(self.solis)
        sum_fields = ['qtde']
        totalize_data(
            self.solis,
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
            'solicitacao', 'pedido_destino', 'qtde'
        ]
        self.context['solis'] = self.table_defs.hfs_dict(*fields)
        self.context['solis'].update({
            'safe': ['solicitacao', 'pedido_destino'],
            'data': self.solis,
            'len': len_solis,
        })

    def mount_solicitacoes(self):
        self.solis = self.get_solis()
        if len(self.solis) > 0:
            self.mount_solis()

    def mount_vars_oti(self):
        solicitacoes = {
            '#': 14,
            2807: 6,
            2856: 45,
            2861: 13,
            2864: 2,
            2876: 27,
            2923: 534,
            2980: 459,
            2981: 27,
            2999: 16,
        }
        lotes = {
            220304159: ('1Q0027', 100),
            230901615: ('1Q0042', 100),
            230901625: ('1Q0042', 100),
            231202127: ('1Q0043', 100),
            224802702: ('1Q0044', 13),
            231202132: ('1Q0044', 100),
            231801970: ('1Q0047', 48),
            231801975: ('1Q0047', 39),
            231202124: ('1Q0052', 100),
            231202125: ('1Q0052', 100),
            231202128: ('1Q0052', 100),
            231202129: ('1Q0052', 100),
            231202130: ('1Q0052', 100),
            231202131: ('1Q0052', 100),
            231202133: ('1Q0052', 100),
        }
        return solicitacoes, lotes

    def mount_rascunho_oti(self):
        solicitacoes, lotes = self.mount_vars_oti()

        print("Solicitações")
        pprint(solicitacoes)
        total_sols = oti_emp.quant_total(solicitacoes)
        print("Total solicitado", total_sols)

        print()
        print("Lotes")
        pprint(lotes)
        total_lotes = oti_emp.quant_total_lotes(lotes)
        print("Total dos lotes", total_lotes)

        qtd_nao_solicitada = total_lotes - total_sols
        print("Quant. não solicitada", qtd_nao_solicitada)

        print()
        print("Inicia nova distribuição")

        print()
        print("Distribuição vazia")
        new_lotes_sols =  oti_emp.inicia_distribuicao(lotes)
        pprint(new_lotes_sols)

        print()
        print("Lotes ordenados para uso")
        lotes_ord = oti_emp.keys_order_by_dict(new_lotes_sols)
        pprint(lotes_ord)

        print()
        print("Definindo quantidade final de lotes a não utilizar")
        oti_emp.lotes_nao_usar(new_lotes_sols, lotes_ord, qtd_nao_solicitada)
        pprint(new_lotes_sols)

        print()
        print("Lotes atendidos com uma solicitação")
        oti_emp.lotes_uma_sol(new_lotes_sols, solicitacoes)
        pprint(new_lotes_sols)
        pprint(solicitacoes)

        print()
        print("Solicitações ordenadas para uso")
        sols_ord = oti_emp.keys_order_by_value(solicitacoes)
        pprint(sols_ord)

        print()
        print("Demais lotes do maior para o menor")
        new_lotes_sols_iter_ord = oti_emp.lotes_parciais(
            new_lotes_sols, lotes_ord, sols_ord, solicitacoes)
        pprint(new_lotes_sols)
        print(oti_emp.conta_zerados(new_lotes_sols), "lotes zerados")

        print()
        print("visão ordenada")
        pprint(new_lotes_sols_iter_ord)

        self.context.update({
            'a_fazer': pformat(new_lotes_sols_iter_ord)
        })

    def filter_inputs(self):
        self.endereco = None if self.endereco == '' else self.endereco
        self.solicitacoes = None if self.solicitacoes == '' else self.solicitacoes
        self.modelo = None if self.modelo == '' else int(self.modelo)
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam
        self.qtd_empenhada = None if self.qtd_empenhada == '' else self.qtd_empenhada
        self.context.update({
            'qtd_empenhada': self.qtd_empenhada,
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.filter_inputs()
        self.mount_lotes_solicitados()
        self.mount_solicitacoes()
        self.mount_lotes_disponiveis()
        self.mount_rascunho_oti()