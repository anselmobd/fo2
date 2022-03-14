from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.views import totalize_data

from lotes.forms.romaneio_corte import RomaneioCorteForm
from lotes.queries.producao.romaneio_corte import query as query_romaneio_corte


class RomaneioCorte(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(RomaneioCorte, self).__init__(*args, **kwargs)
        self.Form_class = RomaneioCorteForm
        self.template_name = 'lotes/romaneio_corte.html'
        self.title_name = 'Romaneio da filial corte'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados = query_romaneio_corte(self.cursor, self.data)

        if not dados:
            return

        for row in dados:
            row['op|TARGET'] = '_blank'
            row['op|LINK'] = reverse(
                'producao:op__get',
                args=[row['op']],
            )
        totalize_data(
            dados,
            {
                'sum': ['lotes', 'qtd', 'perda'],
                'descr': {'data': 'Total:'},
                'row_style': 'font-weight: bold;',
            }
        )

        self.context.update({
            'headers': ['OP', 'Referência', 'Lotes', 'Produzido'],
            'fields': ['op', 'ref', 'lotes', 'qtd'],
            'dados': dados,
            'style': untuple_keys_concat({
                (3, 4): 'text-align: right;',
            }),
        })
