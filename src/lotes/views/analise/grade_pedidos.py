from pprint import pprint

from django.db import connections

from base.forms.forms2 import DepositoForm2
from base.views import O2BaseGetPostView

from lotes.queries.pedido.pedido_faturavel_sortimento \
    import pedido_faturavel_sortimento


class GradePedidos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradePedidos, self).__init__(*args, **kwargs)
        self.Form_class = DepositoForm2
        self.template_name = 'lotes/analise/grade_pedidos.html'
        self.title_name = 'Grade de pedidos a embarcar'
        self.get_args = ['deposito']

    def mount_context(self):
        cursor = connections['so'].cursor()

        deposito = self.form.cleaned_data['deposito']
        self.context.update({
            'deposito': deposito,
        })

        data = pedido_faturavel_sortimento(cursor, None, None)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Depósito não encontrado',
            })
            return
