import datetime
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from geral.functions import has_permission
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

        dados = []
        if self.tipo == 'p':  # Visualiza a produção do estágio 16 na data
            dados = romaneio_corte.produzido_no_dia(self.cursor, self.data)
        elif self.tipo == 'c':  # Visualiza OPs completadas no estágio 16 na data
            dados = romaneio_corte.query_completa(self.cursor, self.data)
        elif self.tipo == 'n':  # Gera pedidos para NF (OPs completadas no estágio 16 na data)
            dados, clientes = romaneio_corte.query_completa(self.cursor, self.data, para_nf=True)
        elif self.tipo == 'g':  # Pedidos gerados para NF
            dados, clientes = romaneio_corte.gerados(self.cursor, self.data)

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
            sum_fields = ['mov_qtd', 'mov_lotes']
            label_tot_field = 'cliente'

            headers = [
                'Cliente',
                ('Pedido<br/>venda<br/>matriz', ),
                ('Código<br/>pedido<br/>cliente', ),
                'OP', 'Item',
                'Quant.', '%Quant.', 'Quant.OP',
                'Lotes', '%Lotes', 'Lotes OP'
            ]
            fields = [
                'cliente', 'ped', 'ped_cli', 'op', 'item',
                'mov_qtd', 'percent_qtd', 'tot_qtd',
                'mov_lotes', 'percent_lotes', 'tot_lotes'
            ]
            style_center = (2, 3)
            style_right = (6, 7, 8, 9, 10, 11)

        elif self.tipo == 'c':
            group = ['cliente']
            sum_fields = ['mov_qtd']
            label_tot_field = 'cliente'

            headers = [
                'Cliente',
                ('Pedido<br/>venda<br/>matriz', ),
                ('Código<br/>pedido<br/>cliente', ),
                'OP',
                'Item',
                'Quant.',
            ]
            fields = [
                'cliente', 'ped', 'ped_cli', 'op', 'item', 'mov_qtd'
            ]
            style_center = (2, 3)
            style_right = (6)

        else:  # if self.tipo == 'n':

            for row in dados:
                if row['pedido_filial'] != '-':
                    row['pedido_filial|TARGET'] = '_blank'
                    row['pedido_filial|LINK'] = reverse(
                        'producao:pedido__get',
                        args=[row['pedido_filial']],
                    )
                    row['pedido_filial'] = ''.join([
                        row['pedido_filial_nf'],
                        str(row['pedido_filial']),
                        row['pedido_filial_quant'],
                    ])
                # if row['pedido_matriz'] == '+':
                #     row['pedido_matriz'] = ""
                #     row['pedido_matriz|GLYPHICON'] = 'glyphicon-plus-sign'
                #     row['pedido_matriz|TARGET'] = '_blank'
                #     row['pedido_matriz|LINK'] = reverse(
                #         'producao:prepara_pedido_compra_matriz',
                #         args=[row['pedido_filial']],
                #     )

            group = ['cliente', 'pedido_filial', 'pedido_matriz', 'obs']
            sum_fields = ['mov_qtd']
            label_tot_field = 'obs'

            headers = [
                'Cliente',
                ('Pedido<br/>venda<br/>filial', ),
                ('Pedido<br/>compra<br/>matriz', ),
                'Observação',
                'Item',
                'Quant.'
            ]
            fields = [
                'cliente',
                'pedido_filial',
                'pedido_matriz',
                'obs',
                'item',
                'mov_qtd'
            ]
            style_center = (1, 2, 3)
            style_right = (6)
            if (self.data < datetime.date.today() and
                has_permission(self.request, 'lotes.prepara_pedidos_filial_matriz')
            ):
                self.context.update({
                    'clientes': {
                        c: clientes[c]['cliente']
                        for c in clientes
                        if clientes[c]['pedido_filial'] == '-'
                    },
                })
            self.context.update({
                'legenda': "Pedido venda filial assinalado com '*' está faturado.",
            })

        totalize_grouped_data(dados, {
            'group': group,
            'sum': sum_fields,
            'count': [],
            'descr': {label_tot_field: 'Totais:'},
            'global_sum': sum_fields,
            'global_descr': {label_tot_field: 'Totais gerais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(dados, group)

        self.context.update({
            'headers': headers,
            'fields': fields,
            'group': group,
            'dados': dados,
            'style': untuple_keys_concat({
                style_center: 'text-align: center;',
                style_right: 'text-align: right;',
            }),
        })
