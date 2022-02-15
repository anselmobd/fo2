from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from lotes.forms.por_celula import PorCelulaForm


class PorCelula(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PorCelula, self).__init__(*args, **kwargs)
        self.Form_class = PorCelulaForm
        self.template_name = 'lotes/por_celula.html'
        self.title_name = 'Produção por célula'
        self.cleaned_data2self = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados = []

        if not dados:
            return

        self.context.update({
            'headers': ['Data', 'Referência', 'Quantidade'],
            'fields': ['data', 'ref', 'qtd'],
            'dados': dados,
        })
