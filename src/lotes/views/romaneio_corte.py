import datetime
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms.romaneio_corte import RomaneioCorteForm
from lotes.queries.producao import romaneio_corte


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

        if self.tipo == 'p':
            dados = romaneio_corte.query(self.cursor, self.data)
        elif self.tipo == 'c':
            dados = romaneio_corte.query_completa(self.cursor, self.data)
        else:  # if self.tipo == 'n':
            dados, clientes = romaneio_corte.query_completa(self.cursor, self.data, nf=True)

        if not dados:
            return

        for row in dados:
            row['op|TARGET'] = '_blank'
            row['op|LINK'] = reverse(
                'producao:op__get',
                args=[row['op']],
            )

        if self.tipo == 'p':
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

        elif self.tipo == 'c':
            group = ['cliente']
            totalize_grouped_data(dados, {
                'group': group,
                'sum': ['mov_qtd'],
                'count': [],
                'descr': {'cliente': 'Totais:'},
                'global_sum': ['mov_qtd'],
                'global_descr': {'cliente': 'Totais gerais:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(dados, group)

            self.context.update({
                'headers': [
                    'Cliente', 'Pedido', 'Cód.Ped.Cliente', 'OP', 'Item', 'Quant.'
                ],
                'fields': [
                    'cliente', 'ped', 'ped_cli', 'op', 'item', 'mov_qtd'
                ],
                'group': group,
                'dados': dados,
                'style': untuple_keys_concat({
                    (2, 3): 'text-align: center;',
                    6: 'text-align: right;',
                }),
            })

        else:  # if self.tipo == 'n':

            group = ['cliente', 'obs']
            totalize_grouped_data(dados, {
                'group': group,
                'sum': ['mov_qtd'],
                'count': [],
                'descr': {'obs': 'Totais:'},
                'global_sum': ['mov_qtd'],
                'global_descr': {'obs': 'Totais gerais:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(dados, group)

            self.context.update({
                'headers': [
                    'Cliente', 'Observação', 'Item', 'Quant.'
                ],
                'fields': [
                    'cliente', 'obs', 'item', 'mov_qtd'
                ],
                'group': group,
                'dados': dados,
                'style': untuple_keys_concat({
                    4: 'text-align: right;',
                }),
            })

            if self.data < datetime.date.today():
                self.context.update({
                    'clientes': dict(enumerate(clientes)),
                })
