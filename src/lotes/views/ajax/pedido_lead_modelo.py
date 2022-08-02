from pprint import pprint

from django.http import JsonResponse

from fo2.connections import db_cursor_so

from geral.functions import config_get_value
from utils.views import totalize_data

from lotes.queries.pedido import faturavel_modelo

import produto.queries


def pedido_lead_modelo(request, modelo):
    cursor = db_cursor_so(request)
    data = {
        'modelo': modelo,
    }
    dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)

    try:
        lead = produto.queries.lead_de_modelo(cursor, modelo)

        if lead == 0:
            periodo = ''
        else:
            periodo = lead + dias_alem_lead

        data_ped = faturavel_modelo.query(
            cursor, modelo=modelo, periodo=':{}'.format(periodo))

        if len(data_ped) == 0:
            total_ped = 0
        else:
            totalize_data(data_ped, {
                'sum': ['QTD'],
                'count': [],
                'descr': {'REF': 'T:'}})
            total_ped = data_ped[-1]['QTD']

    except Exception as e:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar Pedido',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_ped': total_ped,
    })
    return JsonResponse(data, safe=False)
