from pprint import pprint

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2
from o2.views.base.get_post import O2BaseGetPostView

from lotes.queries.analise.produzir_grade_empenho import MountProduzirGradeEmpenho

__all__ = ['ProduzirGradeEmpenho']


class ProduzirGradeEmpenho(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ProduzirGradeEmpenho, self).__init__(*args, **kwargs)
        self.Form_class = Forms2().Modelo
        self.template_name = 'lotes/analise/produzir_grade_empenho.html'
        self.title_name = 'A produzir, por grade, empenho e carteira'
        self.get_args = ['modelo']

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        modelo = self.form.cleaned_data['modelo']
        dados_produzir = MountProduzirGradeEmpenho(cursor, modelo).mount_context()
        self.context.update(dados_produzir)
