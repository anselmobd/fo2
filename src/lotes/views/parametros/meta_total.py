from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView

import comercial.models

from lotes.views.parametros_functions import *


class MetaTotal(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaTotal, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_total.html'
        self.title_name = 'Visualiza total das metas'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        metas = comercial.models.getMetaEstoqueAtual()
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list, total = calculaMetaTotalMetas(cursor, metas)

        self.context.update({
            'data': metas_list,
            'total': total,
        })
