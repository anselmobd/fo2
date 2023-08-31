import operator
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import (
    group_rowspan,
    totalize_grouped_data,
)

from cd.forms.distribuiccao import DistribuicaoForm
from cd.queries.novo_modulo import refs_em_palets


class Distribuicao(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.permission_required = 'cd.can_view_grades_estoque'
        self.Form_class = DistribuicaoForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/distribuicao.html'
        self.title_name = 'Distribuição do estoque'

        self.table_defs = TableDefs(
            {
                'empresa': [],
                'andar': [],
                'lotes': ['Lotes', 'r'],
                'qtd': ['Quantidade', 'r'],
                'param': ['Parâmetro de custo de coleta', 'r'],
                'custo_l': ['Custo*Lote', 'r'],
                'custo_q': ['Custo*Quantidade', 'r'],
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
                }
            por_local[local]['lotes'] += 1
            por_local[local]['qtd'] += row['qtd']

        distr = [
            {
                'empresa': local[0],
                'andar': local[1],
                'param': local[2],
                'lotes': por_local[local]['lotes'],
                'custo_l': local[2] * por_local[local]['lotes'],
                'qtd': por_local[local]['qtd'],
                'custo_q': local[2] * por_local[local]['qtd'],
            }
            for local in por_local 
        ]
        
        distr.sort(key=operator.itemgetter('empresa', 'andar'))
        
        group = ['empresa']
        totalize_grouped_data(distr, {
            'group': group,
            'sum': ['lotes', 'custo_l', 'qtd', 'custo_q'],
            'descr': {'andar': 'Totais:'},
            'global_sum': ['lotes', 'custo_l', 'qtd', 'custo_q'],
            'global_descr': {'andar': 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(distr, group)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': distr,
            'group': group,
            'custo_medio_l': distr[-1]['custo_l'] / distr[-1]['lotes'],
            'custo_medio_q': distr[-1]['custo_q'] / distr[-1]['qtd'],
            'qtd_lote': distr[-1]['qtd'] / distr[-1]['lotes'],
        })


