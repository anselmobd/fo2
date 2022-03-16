from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.views import O2BaseGetView


class Palete(PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Palete, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.can_relocate_lote'
        self.template_name = 'cd/palete.html'
        self.title_name = 'Paletes'
