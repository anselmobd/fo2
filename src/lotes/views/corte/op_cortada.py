import locale
from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
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


class OpCortada(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(OpCortada, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.pode_marcar_op_como_cortada'
        self.Form_class = OpCortadaForm
        self.template_name = 'lotes/corte/op_cortada.html'
        self.title_name = 'Indicação de OP cortada'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def pre_mount_context(self):
        try:
            _ = Colaborador.objects.get(user__username=self.request.user.username)
        except Colaborador.DoesNotExist:
            self.context.update({
                'critical_error': f"Usuário '{self.request.user.username}' "
                                  " não cadastrado como Colaborador.",
            })          

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        dados = op_cortada.query(self.cursor, self.data)

        if not dados:
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

        lista_ops = [
            row['op']
            for row in dados
        ]
        ops_cortadas = Model_OpCortada.objects.filter(op__in=lista_ops).values('op')
        lista_ops_cortadas = [
            str(row['op'])
            for row in ops_cortadas
        ]

        for row in dados:
            row['op'] = f"{row['op']}"
            if row['op'] in op_pedido:
               row['pedido_fm'] = ', '.join(list(op_pedido[row['op']]))
            else:
               row['pedido_fm'] = '-'
            if row['op'] in lista_ops_cortadas:
                row['cortada'] = "Sim"
                row['acao'] = "Desmarca"
            else:
                row['cortada'] = "Não"
                row['acao'] = "Marca"
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
            'OP',
            'Total lotes',
            'Lotes movidos na data',
            'Pedido Filial-Matriz',
            'Corte encerrado?',
            'Ação',
        ]
        fields = [
            'op',
            'lotes',
            'movidos',
            'pedido_fm',
            'cortada',
            'acao',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
        })
