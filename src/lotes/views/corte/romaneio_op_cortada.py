import datetime
import locale
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission
from utils.functions import untuple_keys_concat
from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms.corte.romaneio_op_cortada import RomaneioOpCortadaForm
from lotes.queries.producao.romaneio_corte import (
    pedidos_gerados,
    producao_ops_finalizadas,
    produzido_no_dia,
)


class RomaneioOpCortada(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = RomaneioOpCortadaForm
        self.template_name = 'lotes/corte/romaneio_op_cortada.html'
        self.title_name = 'Romaneio de OPs cortadas'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        dados = []
        if self.tipo == 'p':  # Visualiza a produção do estágio 16 na data
            dados = produzido_no_dia.query(self.cursor, self.data)
        elif self.tipo == 'c':  # Visualiza OPs completadas no estágio 16 na data
            dados = producao_ops_finalizadas.query_base(self.cursor, self.data)
        elif self.tipo == 'n':  # Gera pedidos para NF (OPs completadas no estágio 16 na data)
            dados, clientes = producao_ops_finalizadas.query(self.cursor, self.data, para_nf=True)
            pprint(dados)
            pprint(clientes)
        elif self.tipo == 'g':  # Pedidos gerados para NF e faturados
            dados = pedidos_gerados.query(self.cursor, self.data)
        elif self.tipo == 'a':  # Gera pedidos para NF para OPs apontadas como cortadas pelo Corte
            dados, clientes = producao_ops_finalizadas.query(self.cursor, self.data, para_nf=True)

        if not dados:
            return

        if self.tipo in ('p', 'c'):
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

        elif self.tipo == 'n':

            for row in dados:
                if row['pedido_filial'] != '-':
                    row['pedido_filial|GLYPHICON'] = '_'
                    row['pedido_filial|TARGET'] = '_blank'
                    row['pedido_filial|LINK'] = reverse(
                        'producao:pedido__get',
                        args=[row['pedido_filial']],
                    )
                    row['pedido_filial'] = ''.join([
                        row['pedido_filial_nf'],
                        f"{row['pedido_filial']:n}",
                        row['pedido_filial_quant'],
                    ])
                if row['pedido_matriz'] != '-':
                    row['pedido_matriz'] = ''.join([
                        row['pedido_matriz_nf'],
                        f"{row['pedido_matriz']:n}",
                    ])
                # if row['pedido_matriz'] == '+':
                #     row['pedido_matriz'] = ""
                #     row['pedido_matriz|GLYPHICON'] = 'glyphicon-plus-sign'
                #     row['pedido_matriz|TARGET'] = '_blank'
                #     row['pedido_matriz|LINK'] = reverse(
                #         'producao:prepara_pedido_compra_matriz',
                #         args=[row['pedido_filial']],
                #     )

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

        elif self.tipo == 'g':

            for row in dados:
                if row['pedido_matriz'] == '+':
                    row['pedido_matriz'] = ""
                    row['pedido_matriz|GLYPHICON'] = 'glyphicon-plus-sign'
                    row['pedido_matriz|TARGET'] = '_blank'
                    row['pedido_matriz|LINK'] = reverse(
                        'producao:prepara_pedido_compra_matriz',
                        args=[row['pedido_filial']],
                    )
                else:
                    row['pedido_matriz'] = ''.join([
                        row['pedido_matriz_nf'],
                        f"{row['pedido_matriz']:n}",
                    ])

                row['pedido_filial|GLYPHICON'] = '_'
                row['pedido_filial|TARGET'] = '_blank'
                row['pedido_filial|LINK'] = reverse(
                    'producao:pedido__get',
                    args=[row['pedido_filial']],
                )
                row['pedido_filial'] = ''.join([
                    '*',
                    f"{row['pedido_filial']:n}",
                ])

        if self.tipo in ('n', 'g'):
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

            self.context.update({
                'legenda': "'Pedido venda filial' assinalado com '*' está faturado.<br/>"
                    "'Pedido compra matriz' assinalado com '*' está recebido.",
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
