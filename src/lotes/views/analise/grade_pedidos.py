from pprint import pprint

from django.db import connections

from base.views import O2BaseGetPostView

from lotes.forms.analise import DepositoForm


class GradePedidos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradePedidos, self).__init__(*args, **kwargs)
        self.Form_class = DepositoForm
        self.template_name = 'lotes/analise/grade_pedidos.html'
        self.title_name = 'Grade de pedidos a embarcar'
        self.get_args = ['deposito']

    def mount_context(self):
        cursor = connections['so'].cursor()

        deposito = self.form.cleaned_data['deposito']
        self.context.update({
            'deposito': deposito,
        })

        data = [1]
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Depósito não encontrado',
            })
            return
