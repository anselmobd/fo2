import locale
from pprint import pprint

from django.conf import settings
from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView

from lotes.forms.corte.pedidos_gerados import PedidosGeradosForm
from lotes.models.op import OpComCorte


class PedidosGeradosView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PedidosGeradosView, self).__init__(*args, **kwargs)
        self.Form_class = PedidosGeradosForm
        self.template_name = 'lotes/corte/pedidos_gerados.html'
        self.title_name = 'Pedidos gerados'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True
        self.get_args = ['data']

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        locale.setlocale(locale.LC_ALL, settings.LOCAL_LOCALE)

        dados = OpComCorte.objects.filter(
            pedido_fm_num__isnull=False,
            pedido_fm_quando__date=self.data,
        ).values(
            'pedido_fm_quando',
            'pedido_fm_num',
            'pedido_fm_colab__user__username',
            'op',
            'pedido_cm_num',
        ).order_by(
            '-pedido_fm_quando',
            '-pedido_fm_num',
            '-op',
        )

        for row in dados:
            row['pedido_fm_num'] = f"{row['pedido_fm_num']}"
            row['op'] = f"{row['op']}"
            row['pedido_cm_num'] = f"{row['pedido_cm_num']}"

        headers = [
            'Pedido criado em',
            'Pedido venda filial',
            'Criado por',
            'OP',
            'Pedido compra matriz',
        ]
        fields = [
            'pedido_fm_quando',
            'pedido_fm_num',
            'pedido_fm_colab__user__username',
            'op',
            'pedido_cm_num',
        ]

        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
        })
