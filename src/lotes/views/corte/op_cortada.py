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

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        try:
            _ = Colaborador.objects.get(user__username=self.request.user.username)
        except Colaborador.DoesNotExist:
            self.context.update({
                'err_msg': "Colaborador não cadastrado.",
            })          

        dados = op_cortada.query(self.cursor, self.data)

        if not dados:
            return

        lista_ops = [
            row['op']
            for row in dados
        ]
        ops_cortadas = Model_OpCortada.objects.filter(op__in=lista_ops).values('op')
        lista_ops_cortadas = [
            row['op']
            for row in ops_cortadas
        ]

        for row in dados:
            if row['op'] in lista_ops_cortadas:
                row['cortada'] = "Sim"
                row['acao'] = "Desmarca"
            else:
                row['cortada'] = "Não"
                row['acao'] = "Marca"
            row['acao'] = "Altera"
            row['cortada|CLASS'] = f"cortada op_{row['op']}"
            row['acao|CLASS'] = f"acao op_{row['op']}"
            row['acao|LINK'] = reverse(
                'producao:marca_op_cortada',
                args=[row['op']],
            )

        headers = [
            'OP',
            'Total lotes',
            'Lotes movidos na data',
            'Corte encerrado?',
            'Ação',
        ]
        fields = [
            'op',
            'lotes',
            'movidos',
            'cortada',
            'acao',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
        })
