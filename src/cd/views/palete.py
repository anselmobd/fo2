from pprint import pprint

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from cd.queries.palete import query_palete


class Palete(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'

    def mount_context(self):
        page = self.request.GET.get('page', 1)

        data = query_palete()

        data = paginator_basic(data, 50, page)

        self.context.update({
            'headers': ['Palete'],
            'fields': ['palete'],
            'data': data,
        })
