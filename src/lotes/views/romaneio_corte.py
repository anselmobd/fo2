from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms.romaneio_corte import RomaneioCorteForm
from lotes.queries.producao.romaneio_corte import query2 as query_romaneio_corte


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

        group = ['cliente']
        totalize_grouped_data(dados, {
            'group': group,
            'sum': ['mov_qtd', 'mov_lotes'],
            'count': [],
            'descr': {'cliente': 'Totais:'},
            'global_sum': ['mov_qtd', 'mov_lotes'],
            'global_descr': {'cliente': 'Totais gerais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        self.context.update({
            'headers': [
                'Cliente', 'Pedido', 'Cód.Ped.Cliente', 'OP', 'Item',
                'Quant.', '%Quant.', 'Quant.OP',
                'Lotes', '%Lotes', 'Lotes OP'
            ],
            'fields': [
                'cliente', 'ped', 'ped_cli', 'op', 'item',
                'mov_qtd', 'percent_qtd', 'tot_qtd',
                'mov_lotes', 'percent_lotes', 'tot_lotes'
            ],
            'group': group,
            'dados': dados,
            'style': untuple_keys_concat({
                (2, 3): 'text-align: center;',
                (6, 7, 8, 9, 10, 11): 'text-align: right;',
            }),
        })
