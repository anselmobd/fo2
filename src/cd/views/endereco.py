from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from cd.queries.endereco import query_endereco


class Endereco(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Endereco, self).__init__(*args, **kwargs)
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco.html'
        self.title_name = 'Endereços'

    def mount_context(self):
        page = self.request.GET.get('page', 1)

        data = query_endereco()

        data = paginator_basic(data, 50, page)

        self.context.update({
            'headers': ['Endereço'],
            'fields': ['end'],
            'data': data,
        })
