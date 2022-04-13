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

        data = paginator_basic(data, 50, page)

        self.context.update({
            'headers': [
                'Palete',
                'Endereço',
                'Quant. Lotes',
            ],
            'fields': [
                'cod_container',
                'endereco_container',
                'lotes',
            ],
            'data': data,
        })
