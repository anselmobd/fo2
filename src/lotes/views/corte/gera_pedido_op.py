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

from lotes.forms.corte.gera_pedido_op import GeraPedidoOpForm
from lotes.queries.op import ped_cli_por_cliente


__all__ = ['GeraPedidoOpView']


class GeraPedidoOpView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = GeraPedidoOpForm
        self.template_name = 'lotes/corte/gera_pedido_op.html'
        self.title_name = 'Gera pedidos para OPs'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        clientes = ped_cli_por_cliente.mount_all_and_cache(
            self.cursor, dt=self.data)

        if not clientes:
            return

        cli_dados = []
        for cli_vals in clientes.values():
            row_cli = {
                'cliente': cli_vals['cliente'],
                'obs': cli_vals['obs'],
            }
            for item in cli_vals['itens']:
                row = row_cli.copy()
                row.update(item)
                cli_dados.append(row)

        cli_group = ['cliente', 'obs']
        cli_sum_fields = ['mov_qtd']
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
            'mov_qtd',
        ]
        cli_style_center = (1)
        cli_style_right = (4)

        totalize_grouped_data(cli_dados, {
            'group': cli_group,
            'sum': cli_sum_fields,
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

        if (self.data < datetime.date.today() and
            has_permission(self.request, 'lotes.prepara_pedidos_filial_matriz')
        ):
            self.context.update({
                'clientes': {
                    cliente: clientes[cliente]['cliente']
                    for cliente in clientes
                },
            })
