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

from lotes.forms.corte.op_cortada import OpCortadaForm
from lotes.queries.producao.romaneio_corte import (
    pedidos_gerados,
    producao_ops_finalizadas,
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

        headers = [
            'OP',
            'Total lotes',
            'Lotes movidos na data',
        ]
        fields = [
            'op',
            'lotes',
            'movidos',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
        })
