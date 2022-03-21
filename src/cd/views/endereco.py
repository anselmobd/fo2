from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView

from cd.forms.endereco import EnderecoForm
from cd.queries.endereco import query_endereco


class Endereco(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Endereco, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoForm
        self.form_class_has_initial = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco.html'
        self.title_name = 'Endereços'
        self.cleaned_data2self = True

    def mount_context(self):
        data = query_endereco(self.tipo)

        data = paginator_basic(data, 50, self.page)

        self.context.update({
            'headers': ['Endereço'],
            'fields': ['end'],
            'data': data,
        })
