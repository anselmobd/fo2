import operator
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.table_defs import TableDefs

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

        por_end = {}
        for row in lotes:
            local = get_local(row['endereco'])
            if local not in por_end:
                por_end[local] = {
                    'lotes': 0,
                    'qtd': 0,
                }
            por_end[local]['lotes'] += 1
            por_end[local]['qtd'] += row['qtd']

        pprint(por_end)

        distr = [
            {
                'empresa': local[0],
                'andar': local[1],
                'lotes': por_end[local]['lotes'],
                'qtd': por_end[local]['qtd'],
            }
            for local in por_end 
        ]
        
        pprint(distr)

        distr.sort(key=operator.itemgetter('empresa', 'andar'))
        
        pprint(distr)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': distr,
        })
