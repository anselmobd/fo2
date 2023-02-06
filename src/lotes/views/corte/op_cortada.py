import locale
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission

from lotes.forms.corte.op_cortada import OpCortadaForm
from lotes.models.op import OpCortada as Model_OpCortada
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

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

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
            row['cortada'] = "Sim" if row['op'] in lista_ops_cortadas else "Não"

        headers = [
            'OP',
            'Cortada?',
            'Total lotes',
            'Lotes movidos na data',
        ]
        fields = [
            'op',
            'cortada',
            'lotes',
            'movidos',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
        })
