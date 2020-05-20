from django.db import connections
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetPostView

import comercial
import produto
import lotes
import estoque
from comercial.views.estoque import grade_meta_estoque
from lotes.views.a_produzir import *


class GradePedidos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradePedidos, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.AnaliseModeloForm
        self.template_name = 'lotes/analise/grade_pedidos.html'
        self.title_name = 'Grade de pedidos a embarcar'
        self.get_args = ['deposito']

    def mount_context(self):
        cursor = connections['so'].cursor()

        modelo = self.form.cleaned_data['modelo']
        self.context.update({
            'modelo': modelo,
        })

        data = produto.queries.modelo_inform(cursor, modelo)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return
