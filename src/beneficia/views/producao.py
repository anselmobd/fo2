from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from beneficia.forms import producao


class Producao(O2BaseGetPostView):

    def __init__(self):
        super(Producao, self).__init__()
        self.Form_class = producao.Form
        self.template_name = 'beneficia/producao.html'
        self.title_name = 'Producao'
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        