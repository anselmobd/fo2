from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from produto.forms import ModeloForm

__all__ = ['TagPesquisaView']


class TagPesquisaView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(TagPesquisaView, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm
        self.template_name = 'produto/tag/pesquisa.html'
        self.title_name = 'TAG - Pesquisa'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
