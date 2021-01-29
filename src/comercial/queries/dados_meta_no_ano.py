import datetime
import time
from functools import wraps, partial
from inspect import signature
from pprint import pprint

from django.core.cache import cache
from django.db import connections

from utils.cache import entkeys
from utils.functions import (
    dias_mes_data,
    fo2logger,
    my_make_key_cache,
)

import lotes.queries.pedido as l_q_p

import comercial.models
import comercial.queries


def caching_function(
        func=None, *,
        key_cache_fields=[],
        max_run_delay=20,
        minutes_key_variation=None):
    if func is None:
        return partial(
            caching_function,
            key_cache_fields=key_cache_fields,
            max_run_delay=max_run_delay,
            minutes_key_variation=minutes_key_variation,
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        if minutes_key_variation is not None:
            # nova key a cada x minutos
            now = datetime.datetime.now()
            key_variation = int(
                (now.hour * 60 + now.minute) / minutes_key_variation)

        my_make_key_cache_args = [func.__name__]

        sig = signature(func)
        func_params = list(sig.parameters.keys())
        for field in key_cache_fields:
            field_index = func_params.index(field)
            try:
                value = args[field_index]
            except IndexError:
                value = kwargs[field]
            my_make_key_cache_args.append(value)

        if minutes_key_variation is not None:
            my_make_key_cache_args.append(key_variation)

        key_cache = my_make_key_cache(*my_make_key_cache_args)

        fo2logger.info('antes do while')

        while True:
            fo2logger.info('dentro do while')
            calc_cache = cache.get(f"{key_cache}_calc_", "n")
            if calc_cache == 's':
                fo2logger.info('is _calc_ '+key_cache)
                time.sleep(0.2)
            else:
                fo2logger.info('not _calc_ '+key_cache)
                cached_result = cache.get(key_cache)
                if cached_result is None:
                    fo2logger.info('set _calc_ '+key_cache)
                    cache.set(
                        f"{key_cache}_calc_", "s",
                        timeout=entkeys._SECOND * max_run_delay)
                    break
                else:
                    fo2logger.info('cached '+key_cache)
                    return cached_result

        fo2logger.info('depois do while')

        cached_result = func(*args, **kwargs)

        cache.set(key_cache, cached_result)
        cache.set(f"{key_cache}_calc_", "n")
        fo2logger.info('calculated '+key_cache)

        return cached_result

    return wrapper


@caching_function(key_cache_fields=['hoje'], minutes_key_variation=10)
def dados_meta_no_ano(hoje):
    cursor = connections['so'].cursor()

    ano_atual = hoje.year
    mes_atual = hoje.month
    dia_atual = hoje.day
    dias_mes = dias_mes_data(hoje)

    metas = comercial.models.MetaFaturamento.objects.filter(
        data__year=ano_atual).order_by('data')
    if len(metas) == 0:
        self.context.update({
            'msg_erro': 'Nenhuma meta definida para o ano',
        })
        return

    faturados = comercial.queries.faturamento_para_meta(
        cursor, ano_atual)
    for faturado in faturados:
        faturado['mes'] = int(faturado['mes'][:2])
    faturados_dict = {
        f['mes']: int(round(f['valor']/1000)) for f in faturados
    }

    devolvidos = comercial.queries.devolucao_para_meta(
        cursor, ano_atual)
    for devolvido in devolvidos:
        devolvido['mes'] = int(devolvido['mes'][:2])
    devolvidos_dict = {
        f['mes']: int(round(f['valor']/1000)) for f in devolvidos
    }

    pedidos = l_q_p.pedido_faturavel_modelo(
        cursor, periodo=f'-{dia_atual}:{dias_mes-dia_atual}', nat_oper=(1, 2))
    total_pedido = 0
    for pedido in pedidos:
        total_pedido += pedido['PRECO']
    total_pedido = int(round(total_pedido/1000))

    meses = []
    total = {
        'planejado': 0,
        'faturado': 0,
        'acompensar': 0,
        'compensado': 0,
    }

    compensar = 0
    meses_restantes = 0
    for meta in metas:
        mes = dict(mes=meta.data)
        mes['planejado'] = meta.faturamento
        mes['ajuste'] = meta.ajuste
        mes['imes'] = mes['mes'].month
        mes['faturado'] = (
            faturados_dict.get(mes['imes'], 0) -
            devolvidos_dict.get(mes['imes'], 0)
            )
        if mes['imes'] < mes_atual:
            if mes['planejado'] == 0:
                mes['acompensar'] = mes['ajuste']
                total['acompensar'] += mes['acompensar']
                compensar += - mes['ajuste']
            else:
                mes['acompensar'] = (
                    mes['faturado'] - mes['planejado'])
                total['acompensar'] += mes['acompensar']
                compensar += mes['planejado'] - mes['faturado']
        else:
            meses_restantes += 1
        if mes['imes'] == mes_atual:
            mes['pedido'] = total_pedido
        else:
            mes['pedido'] = 0
        meses.append(mes)
        total['planejado'] += mes['planejado']
        total['faturado'] += mes['faturado']

    for mes in meses:
        if mes['imes'] < mes_atual:
            mes['meta'] = mes['planejado']
        else:
            mes['compensado'] = int(round(compensar / meses_restantes))
            total['compensado'] += mes['compensado']
            mes['meta'] = mes['planejado'] + mes['compensado']

    if compensar != total['compensado']:
        diferenca = compensar - total['compensado']
        passo = int(diferenca / abs(diferenca))

        list_qtds = sorted(
            list({m['planejado'] for m in meses}), reverse=(passo > 0))
        dict_qtds = {}
        for mes in meses:
            qtd = mes['planejado']
            if qtd not in dict_qtds:
                dict_qtds[qtd] = []
            dict_qtds[qtd].append(mes['imes'])

        while passo != 0:
            for qtd in list_qtds:
                for mes_qtd in dict_qtds[qtd]:
                    for mes in meses:
                        if mes['imes'] == mes_qtd and 'compensado' in mes:
                            mes['compensado'] += passo
                            total['compensado'] += passo
                            mes['meta'] += passo
                            diferenca -= passo
                            if diferenca == 0:
                                passo = 0

    for mes in meses:
        if mes['imes'] == mes_atual:
            mes['saldo'] = mes['faturado'] + mes['pedido'] - mes['meta']

        if mes['meta'] == 0:
            mes['percentual'] = 0
        else:
            mes['percentual'] = round(
                (mes['faturado'] + mes['pedido']) / mes['meta'] * 100, 1)

    total['percentual'] = round(
        total['faturado'] / total['planejado'] * 100, 1)

    return meses, total
