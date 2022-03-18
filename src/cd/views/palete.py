from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.views import O2BaseGetView

from cd.queries.palete import query_palete


class Palete(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'

    def mount_context(self):
        data = query_palete()

        self.context.update({
            'headers': ['Palete', 'Etiqueta impressa?'],
            'fields': ['palete', 'impressa'],
            'data': data,
            'ultimo': data[0]['palete'] if data else 'X',
        })
