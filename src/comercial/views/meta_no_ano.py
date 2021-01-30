from pprint import pprint
import datetime

from base.views import O2BaseGetView
from utils.decorators import CacheGet

import comercial.queries


class MetaNoAno(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaNoAno, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/meta_no_ano.html'
        self.title_name = 'Meta do ano'

    def mount_context(self):
        hoje = datetime.date.today()
        mes_atual = hoje.month

        cg = CacheGet()
        msg_erro, meses, total = cg.get_result(
            comercial.queries.dados_meta_no_ano(hoje)
        )

        self.context.update({
            'msg_erro': msg_erro,
            'meses': meses,
            'total': total,
            'mes_atual': mes_atual,
        })
