from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat
from utils.views import totalize_data

from cd.queries.novo_modulo.solicitacoes import get_solicitacoes


class Solicitacoes(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Solicitacoes, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/solicitacoes.html'
        self.title_name = 'Solicitações'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

        data = get_solicitacoes(cursor)

        totalize_data(data, {
            'sum': [
                'l1',
                'q1',
                'l2',
                'q2',
                'l3',
                'q3',
                'l4',
                'q4',
                'l5',
                'q5',
                'lp',
                'qp',
                'lf',
                'qf',
                'lt',
                'qt',
            ],
            'count': [],
            'descr': {'solicitacao': 'Totais:'},
            'row_style': 'font-weight: bold;',
        })

        data = paginator_basic(data, 100, page)

        self.context.update({
            'headers': [
                'Solicitação',
                '1)Lotes',
                '1)Qtd.',
                '2)Lotes',
                '2)Qtd.',
                '3)Lotes',
                '3)Qtd.',
                '4)Lotes',
                '4)Qtd.',
                '5)Lotes',
                '5)Qtd.',
                'Prod.Lotes',
                'Prod.Qtd.',
                'Fin.Lotes',
                'Fin.Qtd.',
                'Tot.Lotes',
                'Tot.Qtd.',
            ],
            'fields': [
                'solicitacao',
                'l1',
                'q1',
                'l2',
                'q2',
                'l3',
                'q3',
                'l4',
                'q4',
                'l5',
                'q5',
                'lp',
                'qp',
                'lf',
                'qf',
                'lt',
                'qt',
            ],
            'style': untuple_keys_concat({
                tuple(range(2, 18)): 'text-align: right;',
            }),
            'data': data,
        })
