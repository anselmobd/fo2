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
                'qtd': ['Qtd.', 'r'],
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
                return ('-', '-')
            if ender.startswith("1Q"):
                return (
                    "Agator",
                    "1º andar" if ender > "1Q0030" else "2º andar"
                )
            else:
                return (
                    "Logyn",
                    f"{ender[3]}º andar"
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
                'lotes': por_local[local]['lotes'],
                'qtd': por_local[local]['qtd'],
            }
            for local in por_local 
        ]
        
        distr.sort(key=operator.itemgetter('empresa', 'andar'))
        
        group = ['empresa']
        totalize_grouped_data(distr, {
            'group': group,
            'sum': ['lotes', 'qtd'],
            'descr': {'andar': 'Totais:'},
            'global_sum': ['lotes', 'qtd'],
            'global_descr': {'andar': 'Totais gerais:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(distr, group)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': distr,
            'group': group,
        })
