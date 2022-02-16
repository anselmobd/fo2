from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.views import group_rowspan

from lotes.forms.por_celula import PorCelulaForm
from lotes.queries.producao.por_celula import query as query_por_celula


class PorCelula(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PorCelula, self).__init__(*args, **kwargs)
        self.Form_class = PorCelulaForm
        self.template_name = 'lotes/por_celula.html'
        self.title_name = 'Produção por célula'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if not self.data_ate:
            self.data_ate = self.data_de

        dados = query_por_celula(
            self.cursor,
            self.data_de,
            self.data_ate,
            self.celula.divisao_producao,
            self.estagio.codigo_estagio,
        )

        if not dados:
            self.context.update({
                'msg_erro': 'Nenhuma produção encontrada',
            })
            return

        group = ['data']
        group_rowspan(dados, group)

        self.context.update({
            'headers': ['Data','OP', 'Referência', 'Lotes', 'Produzido', 'Perda'],
            'fields': ['data', 'op', 'ref', 'lotes', 'qtd', 'perda'],
            'group': group,
            'dados': dados,
            'style': untuple_keys_concat({
                (4, 5, 6): 'text-align: right;',
            }),
        })
