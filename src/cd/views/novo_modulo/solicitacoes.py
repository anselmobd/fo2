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
                'lotes_1',
                'qtde_1',
                'lotes_2',
                'qtde_2',
                'lotes_3',
                'qtde_3',
                'lotes_4',
                'qtde_4',
                'lotes_5',
                'qtde_5',
            ],
            'count': [],
            'descr': {'solicitacao': 'Totais:'},
            'row_style': 'font-weight: bold;',
        })

        data = paginator_basic(data, 100, page)

        self.context.update({
            'headers': [
                'Solicitação',
                'Sit.1 Lotes',
                'Qtd.',
                'Sit.2 Lotes',
                'Qtd.',
                'Sit.3 Lotes',
                'Qtd.',
                'Sit.4 Lotes',
                'Qtd.',
                'Sit.5 Lotes',
                'Qtd.',
            ],
            'fields': [
                'solicitacao',
                'lotes_1',
                'qtde_1',
                'lotes_2',
                'qtde_2',
                'lotes_3',
                'qtde_3',
                'lotes_4',
                'qtde_4',
                'lotes_5',
                'qtde_5',
            ],
            'style': untuple_keys_concat({
                tuple(range(2, 12)): 'text-align: right;',
            }),
            'data': data,
        })
