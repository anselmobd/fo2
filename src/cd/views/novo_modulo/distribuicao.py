from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from cd.forms.distribuiccao import DistribuicaoForm


class Distribuicao(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.permission_required = 'cd.can_view_grades_estoque'
        self.Form_class = DistribuicaoForm
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/distribuicao.html'
        self.title_name = 'Distribuição do estoque'

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
