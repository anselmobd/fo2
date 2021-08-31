from pprint import pprint
import datetime

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.decorators import CacheGet

import comercial.queries


class MetaNoAno(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaNoAno, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/meta_no_ano.html'
        self.title_name = 'Meta do ano'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        hoje = datetime.date.today()  # + datetime.timedelta(days=1)
        mes_atual = hoje.month

        cg = CacheGet()
        msg_erro, meses, total = cg.get_result(
            comercial.queries.dados_meta_no_ano(cursor, hoje)
        )

        # msg_erro, meses, total = comercial.queries.dados_meta_no_ano(cursor, hoje)

        # msg_erro, meses, total = comercial.queries.dados_meta_no_ano(cursor, hoje)

        self.context.update({
            'msg_erro': msg_erro,
            'meses': meses,
            'total': total,
            'mes_atual': mes_atual,
        })
