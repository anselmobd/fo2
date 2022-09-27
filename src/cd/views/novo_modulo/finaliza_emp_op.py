from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from lotes.queries.op import op_aprod

import cd.forms


class FinalizaEmpenhoOp(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FinalizaEmpenhoOp, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.FinalizaEmpenhoOpForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/finaliza_emp_op.html'
        self.title_name = 'Finaliza empenho de OP finalizada'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = op_aprod.query(cursor, self.op)
        pprint(data)
        row = data[0]

        if row['qtd'] is None:
            self.context['mensagem'] = 'OP não encontrada'
            return

        if row['qtd'] != 0:
            self.context['mensagem'] = 'OP não finalizada'
            return

        self.context.update({
            'mensagem': 'Finalizado empenho da OP',
        })
