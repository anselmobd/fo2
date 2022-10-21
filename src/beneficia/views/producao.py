from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from beneficia.forms.producao import Form as ProducaoForm
from beneficia.queries.producao import query as producao_query


class Producao(O2BaseGetPostView):

    def __init__(self):
        super(Producao, self).__init__()
        self.Form_class = ProducaoForm
        self.template_name = 'beneficia/producao.html'
        self.title_name = 'Producao'
        self.form_class_has_initial = True
        self.cleaned_data2self = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        data = producao_query(self.cursor, self.data_de)
        pprint(data)
