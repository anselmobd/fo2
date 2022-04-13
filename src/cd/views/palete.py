from pprint import pprint

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from fo2.connections import db_cursor_so

from cd.queries.palete import get_paletes


class Palete(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

        data = get_paletes(cursor)
        pprint(data[0])

        data = paginator_basic(data, 100, page)

        for row in data:
            if not row['endereco_container']:
                row['endereco_container'] = '-'
            if not row['ultima_inclusao']:
                row['ultima_inclusao'] = '-'

        self.context.update({
            'headers': [
                'Palete',
                'Endereço',
                'Nº Lotes',
                'Última inclusão',
            ],
            'fields': [
                'cod_container',
                'endereco_container',
                'lotes',
                'ultima_inclusao',
            ],
            'data': data,
        })
