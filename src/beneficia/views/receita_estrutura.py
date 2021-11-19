from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from beneficia.forms.main import ReceitaItemForm
from beneficia.queries.receita import receita_estrutura


class ReceitaEstrutura(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ReceitaEstrutura, self).__init__(*args, **kwargs)
        self.Form_class = ReceitaItemForm
        self.template_name = 'beneficia/receita_estrutura.html'
        self.title_name = 'Estrutura de receita'
        self.get_args = ['item']
        self.cleaned_data2self = True

    def mount_context(self):
        if not self.item:
            return
        self.context.update({'render': True})

        self.cursor = db_cursor_so(self.request)

        niv, grup, sub, item = tuple(
            self.item.split('.')
        )
        self.context.update({'receita': grup})

        dados = receita_estrutura(
            self.cursor, niv, grup, sub, item
        )

        if not dados:
            return

        self.context.update({
            'headers': [
                'Seq.', 'Componente', 'Narrativa', 'Alt.',
                'Consumo/Unid.', 'Cálculo', 'Consumo', 'Letra'
            ],
            'fields': [
                'seq', 'comp', 'descr', 'alt',
                'consumo_unidade', 'calculo', 'consumo', 'letra'
            ],
            'dados': dados,
        })
