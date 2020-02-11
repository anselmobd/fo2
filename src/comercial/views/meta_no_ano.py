from pprint import pprint
import datetime

from django.db import connections

from base.views import O2BaseGetView

import comercial.models
import comercial.queries


class MetaNoAno(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaNoAno, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/meta_no_ano.html'
        self.title_name = 'Meta do ano'

    def mount_context(self):
        cursor = connections['so'].cursor()
        hoje = datetime.date.today()
        ano_atual = hoje.year
        mes_atual = hoje.month

        metas = comercial.models.MetaFaturamento.objects.filter(
            data__year=ano_atual)
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma meta definida para o ano',
            })
            return

        faturados = comercial.queries.faturamento_por_mes_no_ano(
            cursor, ano_atual)
        for faturado in faturados:
            faturado['mes'] = int(faturado['mes'][:2])
        faturados_dict = {
            f['mes']: int(f['valor']/1000) for f in faturados
        }

        meses = []
        total = {
            'planejado': 0,
            'faturado': 0,
        }
        compensar = 0
        planejado_restante = 0
        for meta in metas:
            mes = dict(mes=meta.data, planejado=meta.faturamento)
            mes['imes'] = mes['mes'].month
            mes['faturado'] = faturados_dict.get(mes['imes'], 0)
            if mes['imes'] < mes_atual:
                compensar += mes['planejado'] - mes['faturado']
            else:
                planejado_restante += mes['planejado']
            meses.append(mes)
            total['planejado'] += mes['planejado']
            total['faturado'] += mes['faturado']

        for mes in meses:
            if mes['imes'] < mes_atual or compensar < 0:
                mes['meta'] = mes['planejado']
            else:
                mes['meta'] = int(
                    mes['planejado'] + (
                        compensar / planejado_restante * mes['planejado']
                    )
                )
            mes['percentual'] = (
                int(mes['faturado'] / mes['meta'] * 100))

        total['percentual'] = int(total['faturado'] / total['planejado'] * 100)

        self.context.update({
            'meses': meses,
            'total': total,
            'mes_atual': mes_atual,
        })
