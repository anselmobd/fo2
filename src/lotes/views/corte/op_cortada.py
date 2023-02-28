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

        weekday = self.data.isoweekday() % 7
        dada_de = self.data + timedelta(days=-weekday)
        data_ate = dada_de + timedelta(days=6)
        dados_ops_corte = op_cortada.query(
            self.cursor,
            data_de=dada_de,
            data_ate=data_ate,
        )
        self.context.update({
            'data_de': dada_de,
            'data_ate': data_ate,
        })

        anterior = self.data + timedelta(days=-7)
        proxima = self.data + timedelta(days=7)
        self.context.update({
            'anterior': anterior,
            'anterior_txt': anterior.strftime('%d/%m/%Y'),
            'proxima': proxima,
            'proxima_txt': proxima.strftime('%d/%m/%Y'),
        })

        if not dados_ops_corte:
            return

        pedidos_filial = pedidos_filial_na_data(
            self.cursor,
            data_de=self.data,
        )
        op_pedido = {}
        for cliente in pedidos_filial:
            for pedido in pedidos_filial[cliente]:
                for op in pedido['op_ped']:
                    try:
                        op_pedido[op].add(str(pedido['ped']))
                    except KeyError:
                        op_pedido[op] = {str(pedido['ped'])}

        ops_corte = [
            row['op']
            for row in dados_ops_corte
        ]
        ops_cortadas = Model_OpCortada.objects.filter(op__in=ops_corte).values('op')
        lista_ops_cortadas = [
            str(row['op'])
            for row in ops_cortadas
        ]

        for row in dados_ops_corte:
            row['dt_corte'] = row['dt_corte'].date()
            row['op'] = f"{row['op']}"
            if row['op'] in op_pedido:
                row['pedido_fm'] = ', '.join(list(op_pedido[row['op']]))
            else:
                row['pedido_fm'] = '-'
            if row['op'] in lista_ops_cortadas:
                row['cortada'] = "Sim"
                row['cortada|STYLE'] = "color:darkgreen"
            else:
                row['cortada'] = "Não"
                row['cortada|STYLE'] = "color:darkred"
            row['cortada|CLASS'] = f"cortada op_{row['op']}"
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
            'Data',
            'OP',
            'Total lotes',
            'Lotes cortados na semana',
            'Pedido Filial-Matriz',
            'Corte encerrado?',
        ]
        fields = [
            'dt_corte',
            'op',
            'lotes',
            'movidos',
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
            'dados': dados_ops_corte,
            'style': {
                5: "font-weight: bold;",
            }
        })
