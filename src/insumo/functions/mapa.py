import datetime
import math
from operator import itemgetter
from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import (
    fo2logger,
    make_key_cache,
    max_not_None,
    segunda,
)

import insumo.queries as queries


def mapa_por_insumo_dados(cursor, nivel, ref, cor, tam, calc=False):

    def return_result(result):
        cached_result = result
        old_cached_result = None
        if calc:
            old_cached_result = cache.get(key_cache)
        cache.set(key_cache, cached_result, timeout=entkeys._HOUR*14)
        fo2logger.info('calculated '+key_cache)
        if cached_result != old_cached_result:
            entkeys.flush((nivel, ref, cor, tam))
        return cached_result

    key_cache = make_key_cache(ignore=['calc'])
    if not calc:
        cached_result = cache.get(key_cache)
        if cached_result is not None:
            fo2logger.info('cached '+key_cache)
            return cached_result

    datas = {}

    data_id = queries.insumo_descr(cursor, nivel, ref, cor, tam)

    if len(data_id) == 0:
        datas.update({
            'msg_erro': 'Item não encontrado!',
        })
        return return_result(datas)

    dias_reposicao = data_id[0]['REPOSICAO']
    data_id[0]['SEMANAS'] = math.ceil(dias_reposicao / 7)

    qtd_estoque = data_id[0]['QUANT']
    estoque_minimo = data_id[0]['STQ_MIN']
    lote_multiplo = data_id[0]['LOTE_MULTIPLO']

    semana_hoje = segunda(datetime.date.today())

    semana_recebimento = segunda(
        semana_hoje +
        datetime.timedelta(days=dias_reposicao+7))

    datas.update({
        'estoque_minimo': estoque_minimo,
        'semana_recebimento': semana_recebimento,
        'semanas': data_id[0]['SEMANAS'],
    })

    # Necessidades
    data_ins = queries.insumo_necessidade_semana(
        cursor, nivel, ref, cor, tam)

    for row in data_ins:
        row['SEMANA_NECESSIDADE'] = row['SEMANA_NECESSIDADE'].date()

    # Previsões
    data_prev = queries.insumo_previsoes_semana_insumo(
        cursor, nivel, ref, cor, tam)

    for row in data_prev:
        row['DT_NECESSIDADE'] = row['DT_NECESSIDADE'].date()
        row['QTD_ORIGINAL'] = row['QTD']

    # Descontando das necessidades previstas as necessidades reais
    prev_idx = len(data_prev) - 1
    if prev_idx >= 0:
        for ness in reversed(data_ins):
            while prev_idx >= 0:
                if data_prev[prev_idx]['DT_NECESSIDADE'] <= \
                        ness['SEMANA_NECESSIDADE']:
                    data_prev[prev_idx]['QTD'] -= ness['QTD_INSUMO']
                    if data_prev[prev_idx]['QTD'] < 0:
                        data_prev[prev_idx]['QTD'] = 0
                    data_prev[prev_idx]['ITALIC'] = True
                    ness['ITALIC'] = True
                    break
                else:
                    prev_idx -= 1

    # Recebimentos
    data_irs = queries.insumo_recebimento_semana(
        cursor, nivel, ref, cor, tam)

    # Dicionários por semana (sem passado)
    data_ness = [{
        'DT': x['SEMANA_NECESSIDADE'],
        'QTD': x['QTD_INSUMO']
        } for x in data_ins]
    data_ness.extend([{
        'DT': x['DT_NECESSIDADE'],
        'QTD': x['QTD']
        } for x in data_prev])
    data_ness = sorted(data_ness, key=itemgetter('DT'))

    necessidades = {}
    necessidades_passadas = 0
    ult_necessidade = None
    for row in data_ness:
        if row['DT'] < semana_hoje:
            necessidades_passadas += row['QTD']
            ult_necessidade = semana_hoje
        else:
            if row['DT'] in necessidades:
                necessidades[row['DT']] += row['QTD']
            else:
                necessidades[row['DT']] = row['QTD']
            ult_necessidade = row['DT']

    recebimentos = {}
    pri_recebimento = None
    ult_recebimento = None
    recebimentos_atrasados = 0
    for row in data_irs:
        row['SEMANA_ENTREGA'] = row['SEMANA_ENTREGA'].date()
        if row['SEMANA_ENTREGA'] < semana_hoje:
            recebimentos_atrasados += row['QTD_A_RECEBER']
            ult_recebimento = semana_hoje
        else:
            semana = row['SEMANA_ENTREGA']
            if semana in recebimentos:
                recebimentos[semana] += row['QTD_A_RECEBER']
            else:
                recebimentos[semana] = row['QTD_A_RECEBER']
            if pri_recebimento is None:
                pri_recebimento = semana
            ult_recebimento = semana

    semana = semana_hoje

    semana_fim = max_not_None(
        ult_recebimento,
        ult_necessidade)

    datas.update({
        'data_id': data_id,
        'semana_hoje': semana_hoje,
        'data_ins': data_ins,
        'data_prev': data_prev,
        'data_irs': data_irs,
    })

    data_sug = []
    data_adiantamentos = []

    # se não tem entrada ou saída mas o estoque está abaixo do mínimo, força
    # uma semana_fim
    if semana_fim is None and qtd_estoque < estoque_minimo:
        semana_fim = semana_hoje

    # se tem alguma entrada ou saída ou o estoque está abaixo do mínimo
    if semana_fim is not None:
        # criando mapa de compras
        semana_fim += datetime.timedelta(days=7)

        data = []
        estoque = qtd_estoque
        necessidade_passada = necessidades_passadas
        recebimento_atrasado = recebimentos_atrasados
        while semana <= semana_fim:
            recebimento = recebimentos.get(semana, 0)
            necessidade = necessidades.get(semana, 0)
            data.append({
                'DATA': semana,
                'NECESSIDADE': necessidade,
                'NECESSIDADE_PASSADA': necessidade_passada,
                'RECEBIMENTO': recebimento,
                'RECEBIMENTO_ATRASADO': recebimento_atrasado,
                'RECEBIMENTO_MOVIDO': 0,
                'RECEBIMENTO_ADIANTADO': 0,
                'ESTOQUE': estoque,
                'ESTOQUE_IDEAL': estoque,
                'COMPRAR': 0,
                'COMPRAR_PASSADO': 0,
                'RECEBER': 0,
                'RECEBER_IDEAL': 0,
                'RECEBER_IDEAL_ANTES': 0,
            })
            estoque = estoque \
                - necessidade - necessidade_passada \
                + recebimento + recebimento_atrasado

            semana += datetime.timedelta(days=7)
            necessidade_passada = 0
            recebimento_atrasado = 0

        # percorre o mapa de compras para montar sugestões de compra
        for row in data:
            # pega uma sugestão se estoque < mínimo
            sugestao_quatidade = 0
            recebimento_adiantado = 0
            if row['ESTOQUE_IDEAL'] < estoque_minimo:
                sugestao_quatidade = estoque_minimo - row['ESTOQUE_IDEAL']
                if lote_multiplo != 0:
                    qtd_quebrada = sugestao_quatidade % lote_multiplo
                    if qtd_quebrada != 0:
                        qtd_lote_mult = sugestao_quatidade // lote_multiplo
                        qtd_lote_mult += 1
                        sugestao_quatidade = lote_multiplo * qtd_lote_mult
                sugestao_receber = \
                    row['DATA'] + datetime.timedelta(days=-7)
                sugestao_receber_ideal = sugestao_receber
                sugestao_comprar = segunda(
                    sugestao_receber +
                    datetime.timedelta(days=-dias_reposicao))

                # adianta recebimentos que houver
                receb_adianta_dt_destino = \
                    row['DATA'] + datetime.timedelta(days=-7)
                for row_rec in data:
                    if row_rec['DATA'] < row['DATA']:
                        continue
                    recebimento_na_semana = \
                        row_rec['RECEBIMENTO'] - row_rec['RECEBIMENTO_MOVIDO']
                    if recebimento_na_semana > 0:
                        recebimento_a_adiantar = min(
                            sugestao_quatidade, recebimento_na_semana)
                        data_adiantamentos.append({
                            'SEMANA_ORIGEM': row_rec['DATA'],
                            'SEMANA_DESTINO': receb_adianta_dt_destino,
                            'QUANT': recebimento_a_adiantar,
                        })
                        sugestao_quatidade -= recebimento_a_adiantar
                        recebimento_adiantado += recebimento_a_adiantar
                        row_rec['RECEBIMENTO_MOVIDO'] += recebimento_a_adiantar
                        if sugestao_quatidade == 0:
                            break

            # se essa linha do mapa gerou alguma sugestão de compra
            # se sugestão não foi atendida por adiantemanto de recebimento
            if sugestao_quatidade != 0:
                data_sug.append({
                    'SEMANA_COMPRA': sugestao_comprar,
                    'SEMANA_RECEPCAO': sugestao_receber,
                    'QUANT': sugestao_quatidade,
                })

                # se a sugestão á comprar está no passado, mude para hoje
                if sugestao_comprar < semana_hoje:
                    sugestao_comprar_passado = semana_hoje
                else:
                    sugestao_comprar_passado = None

                # se sugestão de compra chega ou passa da última data do
                # mapa de compras, adicionar mais datas
                if semana_fim <= sugestao_receber:
                    semana = semana_fim + datetime.timedelta(days=7)
                    semana_fim = sugestao_receber + datetime.timedelta(
                        days=7)
                    while semana <= semana_fim:
                        data.append({
                            'DATA': semana,
                            'NECESSIDADE': 0,
                            'NECESSIDADE_PASSADA': 0,
                            'RECEBIMENTO': 0,
                            'RECEBIMENTO_ATRASADO': 0,
                            'RECEBIMENTO_MOVIDO': 0,
                            'RECEBIMENTO_ADIANTADO': 0,
                            'ESTOQUE': 0,
                            'ESTOQUE_IDEAL': 0,
                            'COMPRAR': 0,
                            'COMPRAR_PASSADO': 0,
                            'RECEBER': 0,
                            'RECEBER_IDEAL': 0,
                            'RECEBER_IDEAL_ANTES': 0,
                        })
                        semana += datetime.timedelta(days=7)

            # se essa linha do mapa gerou alguma sugestão de compra ou
            # adiantamento de recebimento
            if sugestao_quatidade != 0 or recebimento_adiantado != 0:

                # atualiza o mapa de compras com a sugestão calculada
                # calcula "estoque" e "estoque ideal" (feito com as
                # sugestões ideais)
                estoque = qtd_estoque
                estoque_ideal = qtd_estoque
                for row_recalc in data:

                    if sugestao_quatidade != 0:
                        if row_recalc['DATA'] == sugestao_comprar:
                            row_recalc['COMPRAR'] += sugestao_quatidade
                        if row_recalc['DATA'] == sugestao_comprar_passado:
                            row_recalc['COMPRAR_PASSADO'] += sugestao_quatidade
                        if row_recalc['DATA'] == semana_hoje:
                            if row_recalc['DATA'] >= sugestao_receber:
                                row_recalc['RECEBER'] += sugestao_quatidade
                        else:
                            if row_recalc['DATA'] == sugestao_receber:
                                row_recalc['RECEBER'] += sugestao_quatidade
                        if sugestao_receber_ideal < semana_hoje:
                            if row_recalc['DATA'] == semana_hoje:
                                row_recalc['RECEBER_IDEAL_ANTES'] += \
                                    sugestao_quatidade
                        else:
                            if row_recalc['DATA'] == sugestao_receber_ideal:
                                row_recalc['RECEBER_IDEAL'] += \
                                    sugestao_quatidade

                    if recebimento_adiantado != 0:
                        if row_recalc['DATA'] == receb_adianta_dt_destino:
                            row_recalc['RECEBIMENTO_ADIANTADO'] += \
                                recebimento_adiantado
                        if row_recalc['DATA'] == semana_hoje and \
                                row_recalc['DATA'] > receb_adianta_dt_destino:
                            row_recalc['RECEBIMENTO_ATRASADO'] += \
                                recebimento_adiantado

                    row_recalc['ESTOQUE'] = estoque
                    estoque = estoque \
                        - row_recalc['NECESSIDADE'] \
                        - row_recalc['NECESSIDADE_PASSADA'] \
                        + row_recalc['RECEBIMENTO'] \
                        + row_recalc['RECEBIMENTO_ATRASADO']

                    row_recalc['ESTOQUE_IDEAL'] = \
                        row_recalc['RECEBER_IDEAL_ANTES'] + estoque_ideal
                    estoque_ideal = row_recalc['RECEBER_IDEAL_ANTES'] \
                        + estoque_ideal \
                        - row_recalc['NECESSIDADE'] \
                        - row_recalc['NECESSIDADE_PASSADA'] \
                        + row_recalc['RECEBIMENTO'] \
                        + row_recalc['RECEBIMENTO_ATRASADO'] \
                        - row_recalc['RECEBIMENTO_MOVIDO'] \
                        + row_recalc['RECEBIMENTO_ADIANTADO'] \
                        + row_recalc['RECEBER_IDEAL']
        datas.update({
            'data': data,
        })
    datas.update({
        'data_sug': data_sug,
        'data_adi': data_adiantamentos,
    })
    return return_result(datas)


def new_mapa_por_insumo_dados(cursor, nivel, ref, cor, tam, calc=False):

    def return_result(result):
        cached_result = result
        old_cached_result = None
        if calc:
            old_cached_result = cache.get(key_cache)
        cache.set(key_cache, cached_result, timeout=entkeys._HOUR*14)
        fo2logger.info('calculated '+key_cache)
        if cached_result != old_cached_result:
            entkeys.flush((nivel, ref, cor, tam))
        return cached_result

    key_cache = make_key_cache(ignore=['calc'])
    if not calc:
        cached_result = cache.get(key_cache)
        if cached_result is not None:
            fo2logger.info('cached '+key_cache)
            return cached_result

    datas = {}

    data_id = queries.insumo_descr(cursor, nivel, ref, cor, tam)
    # print('data_id')
    # pprint(data_id)

    if len(data_id) == 0:
        datas.update({
            'msg_erro': 'Item não encontrado!',
        })
        return return_result(datas)

    dias_reposicao = data_id[0]['REPOSICAO']
    data_id[0]['SEMANAS'] = math.ceil(dias_reposicao / 7)

    qtd_estoque = data_id[0]['QUANT']
    estoque_minimo = data_id[0]['STQ_MIN']
    lote_multiplo = data_id[0]['LOTE_MULTIPLO']

    semana_hoje = segunda(datetime.date.today())

    semana_recebimento = segunda(
        semana_hoje +
        datetime.timedelta(days=dias_reposicao+7))

    datas.update({
        'estoque_minimo': estoque_minimo,
        'semana_recebimento': semana_recebimento,
        'semanas': data_id[0]['SEMANAS'],
    })

    # Necessidades
    data_ins = queries.insumo_necessidade_semana(
        cursor, nivel, ref, cor, tam)

    for row in data_ins:
        row['SEMANA_NECESSIDADE'] = row['SEMANA_NECESSIDADE'].date()
    # print('data_ins')
    # pprint(data_ins)

    # Previsões
    data_prev = queries.insumo_previsoes_semana_insumo(
        cursor, nivel, ref, cor, tam)

    for row in data_prev:
        row['DT_NECESSIDADE'] = row['DT_NECESSIDADE'].date()
        row['QTD_ORIGINAL'] = row['QTD']
    # print('data_prev')
    # pprint(data_prev)

    # Descontando das necessidades previstas as necessidades reais
    prev_idx = len(data_prev) - 1
    if prev_idx >= 0:
        for ness in reversed(data_ins):
            while prev_idx >= 0:
                if data_prev[prev_idx]['DT_NECESSIDADE'] <= \
                        ness['SEMANA_NECESSIDADE']:
                    data_prev[prev_idx]['QTD'] -= ness['QTD_INSUMO']
                    if data_prev[prev_idx]['QTD'] < 0:
                        data_prev[prev_idx]['QTD'] = 0
                    data_prev[prev_idx]['ITALIC'] = True
                    ness['ITALIC'] = True
                    break
                else:
                    prev_idx -= 1
    # print('data_prev descontada')
    # pprint(data_prev)

    # Recebimentos
    data_irs = queries.insumo_recebimento_semana(
        cursor, nivel, ref, cor, tam)
    # print('data_irs')
    # pprint(data_irs)

    # Dicionários por semana (sem passado)
    data_ness = [{
        'DT': x['SEMANA_NECESSIDADE'],
        'QTD': x['QTD_INSUMO']
        } for x in data_ins]
    # print('data_ness 1 data_ins')
    # pprint(data_ness)

    data_ness.extend([{
        'DT': x['DT_NECESSIDADE'],
        'QTD': x['QTD']
        } for x in data_prev])
    # print('data_ness 2 data_prev')
    # pprint(data_ness)

    data_ness = sorted(data_ness, key=itemgetter('DT'))
    # print('data_ness 3 sorted')
    # pprint(data_ness)

    necessidades = {}
    necessidades_passadas = 0
    ult_necessidade = None
    for row in data_ness:
        if row['DT'] < semana_hoje:
            necessidades_passadas += row['QTD']
            ult_necessidade = semana_hoje
        else:
            if row['DT'] in necessidades:
                necessidades[row['DT']] += row['QTD']
            else:
                necessidades[row['DT']] = row['QTD']
            ult_necessidade = row['DT']
    # print('necessidades')
    # pprint(necessidades)
    # print('necessidades_passadas', necessidades_passadas)
    # print('ult_necessidade', ult_necessidade)

    recebimentos = {}
    pri_recebimento = None
    ult_recebimento = None
    recebimentos_atrasados = 0
    for row in data_irs:
        row['SEMANA_ENTREGA'] = row['SEMANA_ENTREGA'].date()
        if row['SEMANA_ENTREGA'] < semana_hoje:
            recebimentos_atrasados += row['QTD_A_RECEBER']
            ult_recebimento = semana_hoje
        else:
            semana = row['SEMANA_ENTREGA']
            if semana in recebimentos:
                recebimentos[semana] += row['QTD_A_RECEBER']
            else:
                recebimentos[semana] = row['QTD_A_RECEBER']
            if pri_recebimento is None:
                pri_recebimento = semana
            ult_recebimento = semana
    # print('recebimentos')
    # pprint(recebimentos)
    # print('pri_recebimento', pri_recebimento)
    # print('ult_recebimento', ult_recebimento)
    # print('recebimentos_atrasados', recebimentos_atrasados)

    semana = semana_hoje

    semana_fim = max_not_None(
        ult_recebimento,
        ult_necessidade)
    # print('semana', semana)
    # print('semana_fim', semana_fim)

    datas.update({
        'data_id': data_id,
        'semana_hoje': semana_hoje,
        'data_ins': data_ins,
        'data_prev': data_prev,
        'data_irs': data_irs,
    })

    data_sug = []
    data_receb_descontados = []

    # se não tem entrada ou saída mas o estoque está abaixo do mínimo, força
    # uma semana_fim
    if semana_fim is None and qtd_estoque < estoque_minimo:
        semana_fim = semana_hoje

    # se tem alguma entrada ou saída ou o estoque está abaixo do mínimo
    if semana_fim is not None:
        # criando mapa de compras
        semana_fim += datetime.timedelta(days=7)

        data = []
        necessidade_passada = necessidades_passadas
        recebimento_atrasado = recebimentos_atrasados
        while semana <= semana_fim:
            recebimento = recebimentos.get(semana, 0)
            necessidade = necessidades.get(semana, 0)
            data.append({
                'DATA': semana,
                'ESTOQUE': 0,
                'NECESSIDADE': necessidade,
                'NECESSIDADE_PASSADA': necessidade_passada,
                'RECEBIMENTO': recebimento,
                'RECEBIMENTO_ATRASADO': recebimento_atrasado,
                'RECEBIMENTO_MOVIDO': 0,
                'COMPRAR': 0,
                'COMPRAR_PASSADO': 0,
                'RECEBER': 0,
            })
            semana += datetime.timedelta(days=7)
            necessidade_passada = 0
            recebimento_atrasado = 0

        recalc_estoque(data, qtd_estoque)

        print('data inicializada')
        print_data(data)

        # percorre o mapa de compras para montar sugestões de compra
        for index_principal in range(len(data)):
            row = data[index_principal]
            print('row inicio')
            pprint(row['DATA'])

            # pega uma sugestão se estoque < mínimo
            sugestao_quatidade = 0
            total_receb_descontado = 0
            estoque_final_semana = calc_estoque_final_semana(row)
            if estoque_final_semana < estoque_minimo:
                print('estoque_final_semana abaixo do estoque mínimo',
                      estoque_minimo)
                sugestao_quatidade = estoque_minimo - estoque_final_semana
                if lote_multiplo != 0:
                    qtd_quebrada = sugestao_quatidade % lote_multiplo
                    if qtd_quebrada != 0:
                        qtd_lote_mult = sugestao_quatidade // lote_multiplo
                        qtd_lote_mult += 1
                        sugestao_quatidade = lote_multiplo * qtd_lote_mult
                sugestao_semana_recepcao = row['DATA']
                sugestao_semana_comprar = segunda(
                    sugestao_semana_recepcao +
                    datetime.timedelta(days=-dias_reposicao))

                print('sugestao_quatidade', sugestao_quatidade)
                print('sugestao_semana_comprar', sugestao_semana_comprar)
                print('sugestao_semana_recepcao', sugestao_semana_recepcao)
                print('total_receb_descontado', total_receb_descontado)

                # adianta recebimentos que houver
                for row_rec in data:
                    if row_rec['DATA'] <= row['DATA']:
                        continue
                    if row_rec['RECEBIMENTO'] > 0:
                        recebimento_a_descontar = min(
                            sugestao_quatidade, row_rec['RECEBIMENTO'])
                        data_receb_descontados.append({
                            'SEMANA_ORIGEM': row_rec['DATA'],
                            'SEMANA_DESTINO': sugestao_semana_recepcao,
                            'QUANT': recebimento_a_descontar,
                        })
                        print('data_receb_descontados')
                        pprint(data_receb_descontados[-1])
                        sugestao_quatidade -= recebimento_a_descontar
                        total_receb_descontado += recebimento_a_descontar

                        # posiciona movimentação de recebimentos no mapa
                        for row_recebimentos in data:
                            if row_recebimentos['DATA'] == row_rec['DATA']:
                                row_recebimentos['RECEBIMENTO'] -= \
                                    recebimento_a_descontar

                            if (row_recebimentos['DATA'] ==
                                    sugestao_semana_recepcao):
                                row_recebimentos['RECEBIMENTO_MOVIDO'] += \
                                    recebimento_a_descontar

                        if sugestao_quatidade == 0:
                            break
                print('sugestao_quatidade 2', sugestao_quatidade)
                print('total_receb_descontado 2', total_receb_descontado)

            # se essa linha do mapa gerou alguma sugestão de compra
            # se sugestão não foi atendida por adiantemanto de recebimento
            if sugestao_quatidade != 0:
                print('sugestao_quatidade não ZERO')
                data_sug.append({
                    'SEMANA_COMPRA': sugestao_semana_comprar,
                    'SEMANA_RECEPCAO': sugestao_semana_recepcao,
                    'QUANT': sugestao_quatidade,
                })
                pprint(data_sug[-1])

                # se sugestão de compra chega ou passa da última data do
                # mapa de compras, adicionar mais datas
                if semana_fim <= sugestao_semana_recepcao:
                    semana = semana_fim + datetime.timedelta(days=7)
                    semana_fim = sugestao_semana_recepcao + datetime.timedelta(
                        days=7)
                    while semana <= semana_fim:
                        data.append({
                            'DATA': semana,
                            'ESTOQUE': 0,
                            'NECESSIDADE': 0,
                            'NECESSIDADE_PASSADA': 0,
                            'RECEBIMENTO': 0,
                            'RECEBIMENTO_ATRASADO': 0,
                            'RECEBIMENTO_MOVIDO': 0,
                            'COMPRAR': 0,
                            'COMPRAR_PASSADO': 0,
                            'RECEBER': 0,
                        })
                        semana += datetime.timedelta(days=7)

                # posiciona sugestão no mapa
                for row_sugestao in data:
                    if sugestao_semana_comprar < semana_hoje:
                        if row_sugestao['DATA'] == semana_hoje:
                            row_sugestao['COMPRAR_PASSADO'] += \
                                sugestao_quatidade

                    else:
                        if row_sugestao['DATA'] == sugestao_semana_comprar:
                            row_sugestao['COMPRAR'] += \
                                sugestao_quatidade

                    if row_sugestao['DATA'] == sugestao_semana_recepcao:
                        row_sugestao['RECEBER'] += \
                            sugestao_quatidade

            if sugestao_quatidade != 0 or total_receb_descontado != 0:
                recalc_estoque(data, qtd_estoque)

            print('data atualizada')
            print_data(data)

            # if index_principal == 3:
            #     break

        datas.update({
            'data': data,
        })

    datas.update({
        'data_sug': data_sug,
        'data_adi': data_receb_descontados,
    })
    return return_result(datas)


def calc_estoque_final_semana(row, com_receber=True):
    estoque = row['ESTOQUE'] \
        - row['NECESSIDADE'] \
        - row['NECESSIDADE_PASSADA'] \
        + row['RECEBIMENTO'] \
        + row['RECEBIMENTO_ATRASADO'] \
        + row['RECEBIMENTO_MOVIDO']
    if com_receber:
        estoque += row['RECEBER']
    return estoque


def recalc_estoque(data, qtd_estoque):
    estoque = qtd_estoque
    for row in data:
        row['ESTOQUE'] = estoque
        estoque = calc_estoque_final_semana(row)


def print_data(data):
    print(
        'Semana    ',
        'Estoque Real',
        'Necessidade',
        'Necessidade passada',
        'Recebimento',
        'Recebimento atrasado',
        'Recebimento movido',
        'Compra sugerida',
        'Compra atrasada',
        'Recebimento sugerido',
    )
    for row in data:
        print(
            f"{row['DATA']}",
            f"{row['ESTOQUE']:12.2f}",
            f"{row['NECESSIDADE']:11.2f}",
            f"{row['NECESSIDADE_PASSADA']:19.2f}",
            f"{row['RECEBIMENTO']:11.2f}",
            f"{row['RECEBIMENTO_ATRASADO']:20.2f}",
            f"{row['RECEBIMENTO_MOVIDO']:18.2f}",
            f"{row['COMPRAR']:15.2f}",
            f"{row['COMPRAR_PASSADO']:15.2f}",
            f"{row['RECEBER']:20.2f}",
        )
