from pprint import pprint

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from fo2.connections import db_cursor_so

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

        data = paginator_basic(data, 100, page)

        self.context.update({
            'headers': [
                'Solicitação',
            ],
            'fields': [
                'solicitacao',
            ],
            'data': data,
        })
