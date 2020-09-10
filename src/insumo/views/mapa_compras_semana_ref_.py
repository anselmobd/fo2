import datetime
import math
from pprint import pprint

from django.db import connections
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import my_make_key_cache, fo2logger

import insumo.functions


def mapa_compras_semana_ref(request, item, dtini, qtdsem):

    def return_result(result):
        cached_result = result
        cache.set(key_cache, cached_result, timeout=entkeys._DAY*10)
        fo2logger.info('calculated '+key_cache)
        entkeys.add(key_cache, (nivel, ref, cor, tam), timeout=entkeys._DAY*10)
        return cached_result

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'mapa_compras_semana_ref', item, dtini, qtdsem)
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    template_name = 'insumo/mapa_compras_semana_ref.html'

    nivel = item[0]
    ref = item[2:7]
    cor = item[8:14]
    tam = item[15:18]
    context = {
        'qtdsem': int(qtdsem),
    }

    if len(item) == 2:
        context['th'] = True
    else:
        cursor = connections['so'].cursor()

        data = []

        datas = insumo.functions.mapa_compras_semana_ref_dados(
            cursor, nivel, ref, cor, tam)

        if 'msg_erro' in datas:
            context.update({
                'data': data,
            })
            html = render_to_string(template_name, context)
            return HttpResponse(html)

        data_id = datas['data_id']
        drow = data_id[0]

        drow['REF'] = drow['REF'] + ' (' + drow['DESCR'] + ')'
        drow['COR'] = drow['COR'] + ' (' + drow['DESCR_COR'] + ')'
        if drow['TAM'] != drow['DESCR_TAM']:
            drow['TAM'] = drow['TAM'] + ' (' + drow['DESCR_TAM'] + ')'
        semanas = math.ceil(drow['REPOSICAO'] / 7)
        drow['REP_STR'] = '{}d.({}s.)'.format(drow['REPOSICAO'], semanas)
        drow['QUANT'] = round(drow['QUANT'])

        data_sug = datas['data_sug']
        semana_hoje = datas['semana_hoje']
        semana_recebimento = datas['semana_recebimento']
        dtsem = datetime.datetime.strptime(dtini, '%Y%m%d').date()

        data_adi = datas['data_adi']

        for i in range(int(qtdsem)):
            compra_atrasada = 0
            comprar = 0
            dt_compra = dtsem
            dt_chegada = None

            if len(data_sug) != 0:
                for row in data_sug:
                    if dtsem == semana_hoje and \
                            row['SEMANA_COMPRA'] < semana_hoje:
                        compra_atrasada += row['QUANT']
                        dt_compra = semana_hoje
                        dt_chegada = semana_recebimento
                    if row['SEMANA_COMPRA'] == dtsem:
                        comprar += row['QUANT']
                        dt_chegada = row['SEMANA_RECEPCAO']
                comprar = round(comprar)
                compra_atrasada = round(compra_atrasada)

            movido = round(sum(
                item['QUANT']
                for item in data_adi
                if item['SEMANA_DESTINO'] == dtsem))

            if dt_chegada is None:
                dt_chegada = '-'

            row = drow.copy()

            row.update({
                'nivel': nivel,
                'ref': ref,
                'cor': cor,
                'tam': tam,
                'tam_order': tam.zfill(3),
                'i': i+1,
                'compra_atrasada': compra_atrasada,
                'comprar': comprar,
                'compra_total': compra_atrasada + comprar,
                'dt_compra': dt_compra,
                'dt_chegada': dt_chegada,
                'movido': movido,
            })

            data.append(row)

            dtsem += datetime.timedelta(days=7)

        context.update({
            'data': data,
        })

    html = render_to_string(template_name, context)
    result = HttpResponse(html)
    return return_result(result)
