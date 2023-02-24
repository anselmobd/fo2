import datetime
import locale
from collections import OrderedDict
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission
from utils.functions import untuple_keys_concat
from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms.corte.romaneio_op_cortada import RomaneioOpCortadaForm
from lotes.models.op import OpCortada
from lotes.queries.producao.romaneio_corte import (
    producao_ops_finalizadas,
)
from lotes.queries.op import (
    op_itens,
    op_ped_cli,
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

    def ped_cli_por_cliente(self, pedidos_ops, itens_ops):
        # Separa OPs por clientes e pedidos
        clientes = {}
        for pedido_op in pedidos_ops:
            slug = pedido_op['cliente_slug']
            if slug not in clientes:
                clientes[slug] = {
                    'cliente': pedido_op['cliente'],
                    'pedidos': {},
                    'ops': set(),
                }
            pedidos_do_cliente = clientes[slug]['pedidos']
            if pedido_op['ped_cli'] not in pedidos_do_cliente:
                pedidos_do_cliente[pedido_op['ped_cli']] = {pedido_op['op']}
            else:
                pedidos_do_cliente[pedido_op['ped_cli']].add(pedido_op['op'])
            clientes[slug]['ops'].add(pedido_op['op'])
        # Monta dados para pedido de faturamento filial-matriz
        for cli in clientes:
            cli_dict = clientes[cli]
            # Monta observação
            if cli == 'estoque':
                ops = ', '.join(map(str, cli_dict['pedidos']['-']))
                cli_dict['obs'] = f"OP({ops})"
            else:
                cli_dict['obs'] = ''
                sep = ''
                for ped in cli_dict['pedidos']:
                    ops = ', '.join(map(str, cli_dict['pedidos'][ped]))
                    cli_dict['obs'] += sep + f"Pedido({ped})-OP({ops})"
                    sep = ', '
            # Monta itens
            itens_ops_cli = [
                item_ops
                for item_ops in itens_ops
                if item_ops['op'] in cli_dict['ops']
            ]
            cli_dict['itens'] = OrderedDict()
            for item_op in itens_ops_cli:
                try:
                    cli_dict['itens'][item_op['item']] += item_op['qtd']
                except KeyError:
                    cli_dict['itens'][item_op['item']] = item_op['qtd']
        return clientes

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        dados_ops = OpCortada.objects.filter(when__date__lte=self.data)
        print(dados_ops.query)
        dados_ops = dados_ops.values()
        pprint(dados_ops)
        ops = [
            row['op']
            for row in dados_ops
        ]
        pprint(ops)

        itens_ops = op_itens.query(self.cursor, op=ops)
        pprint(itens_ops)

        ped_cli_ops = op_ped_cli.query(self.cursor, op=ops)
        pprint(ped_cli_ops)

        clientes = self.ped_cli_por_cliente(ped_cli_ops, itens_ops)
        pprint(clientes)

        cli_dados = []
        for cli_vals in clientes.values():
            row_cli = {
                'cliente': cli_vals['cliente'],
                'obs': cli_vals['obs'],
            }
            pprint(cli_vals['itens'])
            for item in cli_vals['itens']:
                pprint(item)
                row = row_cli.copy()
                row['item'] = item
                row['qtd'] = cli_vals['itens'][item]
                cli_dados.append(row)

        cli_group = ['cliente', 'obs']
        cli_sum_fields = ['qtd']
        cli_label_tot_field = 'obs'

        cli_headers = [
            'Cliente',
            'Observação',
            'Item',
            'Quant.',
        ]
        cli_fields = [
            'cliente',
            'obs',
            'item',
            'qtd',
        ]
        cli_style_center = (1)
        cli_style_right = (4)

        totalize_grouped_data(cli_dados, {
            'group': cli_group,
            'sum': cli_sum_fields,
            'count': [],
            'descr': {cli_label_tot_field: 'Totais:'},
            'global_sum': cli_sum_fields,
            'global_descr': {cli_label_tot_field: 'Totais gerais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(cli_dados, cli_group)

        self.context['teste'] = {
            'headers': cli_headers,
            'fields': cli_fields,
            'group': cli_group,
            'dados': cli_dados,
            'style': untuple_keys_concat({
                cli_style_center: 'text-align: center;',
                cli_style_right: 'text-align: right;',
            }),
        }

        dados = []
        dados, clientes = producao_ops_finalizadas.query(self.cursor, self.data, para_nf=True)
        pprint(dados[:2])
        pprint(clientes)

        if not dados:
            return

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
