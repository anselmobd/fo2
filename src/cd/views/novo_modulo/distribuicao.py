import operator
from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import (
    group_rowspan,
    totalize_grouped_data,
)

from cd.forms.distribuiccao import DistribuicaoForm
from cd.queries.novo_modulo import refs_em_palets


class Distribuicao(O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = DistribuicaoForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/distribuicao.html'
        self.title_name = 'Distribuição do estoque'

        self.table_defs = TableDefs(
            {
                'empresa': [],
                'andar': [],
                'param': ['Custo', 'r'],
                'lotes': ['Lotes', 'r'],
                'custo_l': ['C.Lote', 'r'],
                'qtd': ['Quantidade', 'r'],
                'custo_q': ['C.Quantidade', 'r'],
                'lotes_total_emp': ['Tot.E.Lotes', 'r'],
                'custo_lte': ['C.Tot.E.Lotes', 'r'],
                'qtd_total_emp': ['Tot.E.Qtd.', 'r'],
                'custo_qte': ['C.Tot.E.Qtd.', 'r'],
                'lotes_parcial_emp': ['Parc.E.Lotes', 'r'],
                'custo_lpe': ['C.Parc.E.Lotes', 'r'],
                'qtd_parcial_emp': ['Parc.E.Qtd.', 'r'],
                'custo_qpe': ['C.Parc.E.Qtd.', 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        lotes = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            modelo=None if self.modelo == '' else int(self.modelo),
        )

        def get_local(ender):
            if not ender or ender == '-':
                return ('-', '-', 9)
            if ender.startswith("1Q"):
                return (
                    "Agator",
                    "1º andar" if ender > "1Q0030" else "2º andar",
                    2 if ender > "1Q0030" else 3,
                )
            else:
                custo_login = {
                    '1': 1,
                    '2': 3,
                    '3': 4,
                    '4': 6,
                }
                return (
                    "Logyn",
                    f"{ender[3]}º andar",
                    custo_login[ender[3]]
                )

        por_local = {}
        for row in lotes:
            local = get_local(row['endereco'])
            if local not in por_local:
                por_local[local] = {
                    'lotes': 0,
                    'qtd': 0,
                    'lotes_total_emp': 0,
                    'qtd_total_emp': 0,
                    'lotes_parcial_emp': 0,
                    'qtd_parcial_emp': 0,
                }
            por_local[local]['lotes'] += 1
            por_local[local]['qtd'] += row['qtd']
            if row['qtd_emp'] + row['qtd_sol'] > 0:
                if row['qtd_emp'] + row['qtd_sol'] < row['qtd']:
                    por_local[local]['lotes_parcial_emp'] += 1
                    por_local[local]['qtd_parcial_emp'] += row['qtd_emp'] + row['qtd_sol']
                else:
                    por_local[local]['lotes_total_emp'] += 1
                    por_local[local]['qtd_total_emp'] += row['qtd_emp'] + row['qtd_sol']

        distr = [
            {
                'empresa': local[0],
                'andar': local[1],
                'param': local[2],
                'lotes': por_local[local]['lotes'],
                'custo_l': local[2] * por_local[local]['lotes'],
                'qtd': por_local[local]['qtd'],
                'custo_q': local[2] * por_local[local]['qtd'],
                'lotes_total_emp': por_local[local]['lotes_total_emp'],
                'custo_lte': local[2] * por_local[local]['lotes_total_emp'],
                'qtd_total_emp': por_local[local]['qtd_total_emp'],
                'custo_qte': local[2] * por_local[local]['qtd_total_emp'],
                'lotes_parcial_emp': por_local[local]['lotes_parcial_emp'],
                'custo_lpe': local[2] * 2 * por_local[local]['lotes_parcial_emp'],
                'qtd_parcial_emp': por_local[local]['qtd_parcial_emp'],
                'custo_qpe': local[2] * 2 * por_local[local]['qtd_parcial_emp'],
            }
            for local in por_local 
        ]
        
        distr.sort(key=operator.itemgetter('empresa', 'andar'))
        
        group = ['empresa']
        sum = [
            'lotes', 'custo_l', 'qtd', 'custo_q',
            'lotes_total_emp', 'custo_lte', 'qtd_total_emp', 'custo_qte',
            'lotes_parcial_emp', 'custo_lpe', 'qtd_parcial_emp', 'custo_qpe',
        ]
        totalize_grouped_data(distr, {
            'group': group,
            'sum': sum,
            'descr': {'andar': 'Totais:'},
            'global_sum': sum,
            'global_descr': {'andar': 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(distr, group)

        custo_medio_l = distr[-1]['custo_l'] / distr[-1]['lotes']
        custo_medio_q = distr[-1]['custo_q'] / distr[-1]['qtd']

        custo_medio_el = (
            (distr[-1]['custo_lte'] + distr[-1]['custo_lpe'])
            / (distr[-1]['lotes_total_emp'] + distr[-1]['lotes_parcial_emp'])
        ) if (distr[-1]['lotes_total_emp'] + distr[-1]['lotes_parcial_emp']) else 0
        custo_medio_eq = (
            (distr[-1]['custo_qte'] + distr[-1]['custo_qpe'])
            / (distr[-1]['qtd_total_emp'] + distr[-1]['qtd_parcial_emp'])
        ) if (distr[-1]['qtd_total_emp'] + distr[-1]['qtd_parcial_emp']) else 0

        qtd_lote = distr[-1]['qtd'] / distr[-1]['lotes']

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': distr,
            'group': group,
            'custo_medio_l': custo_medio_l,
            'custo_medio_q': custo_medio_q,
            'custo_medio_el': custo_medio_el,
            'custo_medio_eq': custo_medio_eq,
            'qtd_lote': qtd_lote,
        })


