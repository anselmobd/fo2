from pprint import pprint

from django.db import connections

from base.forms.forms2 import DepositoDatasForm2
from base.views import O2BaseGetPostView

from lotes.queries.pedido.pedido_faturavel_sortimento \
    import pedido_faturavel_sortimento


class GradePedidos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradePedidos, self).__init__(*args, **kwargs)
        self.Form_class = DepositoDatasForm2
        self.template_name = 'lotes/analise/grade_pedidos.html'
        self.title_name = 'Grade de pedidos a embarcar'
        self.get_args = ['deposito']

    def mount_context(self):
        cursor = connections['so'].cursor()

        deposito = self.form.cleaned_data['deposito']
        data_de = self.form.cleaned_data['data_de']
        data_ate = self.form.cleaned_data['data_ate']
        self.context.update({
            'deposito': deposito,
            'data_de': data_de,
            'data_ate': data_ate,
        })

        data = pedido_faturavel_sortimento(cursor, deposito, data_de, data_ate)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Pedidos não encontrados',
            })
            return

        self.context.update({
            'headers': ['Referência', 'Cor', 'Tamanho', 'Quantidade'],
            'fields': ['ref', 'cor', 'tam', 'qtd'],
            'data': data,
            'style': {
                4: 'text-align: right;',
            },
        })
