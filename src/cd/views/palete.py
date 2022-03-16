from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.views import O2BaseGetView

from cd.queries.palete import query_pallete


class Palete(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.can_admin_pallet'
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'

    def mount_context(self):
        data = query_pallete()

        self.context.update({
            'headers': ['Palete'],
            'fields': ['palete'],
            'data': data,
        })
