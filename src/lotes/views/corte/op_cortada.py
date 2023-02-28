import locale
from datetime import timedelta
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission

from base.models import Colaborador

from lotes.forms.corte.op_cortada import OpCortadaForm
from lotes.models.op import OpCortada as Model_OpCortada
from lotes.queries.pedido.pedido_filial import (
    pedidos_filial_na_data,
)
from lotes.queries.producao.romaneio_corte import (
    op_cortada,
)


class OpCortada(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(OpCortada, self).__init__(*args, **kwargs)
        self.Form_class = OpCortadaForm
        self.template_name = 'lotes/corte/op_cortada.html'
        self.title_name = 'Indicação de OP cortada'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True
        self.get_args = ['data']

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        anterior = self.data + timedelta(days=-7)
        proxima = self.data + timedelta(days=7)
        self.context.update({
            'anterior': anterior,
            'proxima': proxima,
        })

        weekday = self.data.isoweekday() % 7
        dada_de = self.data + timedelta(days=-weekday)
        data_ate = dada_de + timedelta(days=6)
        self.context.update({
            'data_de': dada_de,
            'data_ate': data_ate,
        })

        dados_ops_cortadas = op_cortada.query(
            self.cursor,
            data_de=dada_de,
            data_ate=data_ate,
        )

        if not dados_ops_cortadas:
            return

        clientes_pedidos_filial = pedidos_filial_na_data(
            self.cursor,
            data_de=dada_de,
        )
        op_pedido = {}
        for cliente in clientes_pedidos_filial:
            pedidos_filial = clientes_pedidos_filial[cliente]
            for pedido in pedidos_filial:
                for op in pedido['op_ped']:
                    try:
                        op_pedido[op].add(str(pedido['ped']))
                    except KeyError:
                        op_pedido[op] = {str(pedido['ped'])}

        ops_cortadas = [
            row['op']
            for row in dados_ops_cortadas
        ]
        dados_ops_marcadas = Model_OpCortada.objects.filter(
            op__in=ops_cortadas).values(
            'op', 'pedido_filial')
        dict_ops_marcadas = {
            str(row['op']): row
            for row in dados_ops_marcadas
        }

        for row in dados_ops_cortadas:
            row['op'] = f"{row['op']}"
            row['dt_corte'] = row['dt_corte'].date()
            if row['op'] in dict_ops_marcadas:
                row['cortada'] = "Sim"
                row['cortada|STYLE'] = "color:darkgreen"
                pedido_filial = dict_ops_marcadas[row['op']]['pedido_filial']
                pedido_fm = [f"<{pedido_filial}>"]
            else:
                row['cortada'] = "Não"
                row['cortada|STYLE'] = "color:darkred"
                pedido_fm = []
            row['cortada|CLASS'] = f"cortada op_{row['op']}"
            if row['op'] in op_pedido:
                pedido_fm = pedido_fm + list(op_pedido[row['op']])
            row['pedido_fm'] = ', '.join(map(str, pedido_fm)) if pedido_fm else '-'
            if row['pedido_fm'] == '-':
                row['acao'] = "Altera"
                row['acao|CLASS'] = f"acao op_{row['op']}"
                row['acao|LINK'] = reverse(
                    'producao:marca_op_cortada',
                    args=[row['op']],
                )
            else:
                row['acao'] = "-"

        headers = [
            'Data final',
            'OP',
            'Total lotes',
            'Lotes cortados',
            'Pedido Filial-Matriz',
            'Corte encerrado?',
        ]
        fields = [
            'dt_corte',
            'op',
            'lotes',
            'cortados',
            'pedido_fm',
            'cortada',
        ]
        if has_permission(self.request, 'cd.can_del_lote_de_palete'):
            try:
                _ = Colaborador.objects.get(user__username=self.request.user.username)
                headers.append('Ação')
                fields.append('acao')
            except Colaborador.DoesNotExist:
                self.context.update({
                    'hint_colaborador': f"Usuário '{self.request.user.username}' "
                                    "não cadastrado como Colaborador.",
                })

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados_ops_cortadas,
            'style': {
                6: "font-weight: bold;",
            }
        })
