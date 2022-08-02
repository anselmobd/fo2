from pprint import pprint

from django.core.cache import cache

from utils.decorators import caching_function
from utils.functions import dias_mes_data

from lotes.queries.pedido import faturavel_modelo

import comercial.models
import comercial.queries
import comercial.queries.devolucao_para_meta


def dados_meta_no_ano_control(cursor, hoje, cached=True):
    key_cache = 'dados_meta_no_ano_control'
    if cached:
        result = cache.get(key_cache)
        if result is None:
            result = dados_meta_no_ano_control(cursor, hoje, cached=False)
    else:
        result = dados_meta_no_ano(cursor, hoje)
        cache.set(key_cache, result, timeout=None)
    return result


# @caching_function(
#     key_cache_fields=['hoje'], 
#     minutes_key_variation=10, 
#     version_key_variation=1,
#     caching_params=True,
# )
def dados_meta_no_ano(cursor, hoje):
    ano_atual = hoje.year
    mes_atual = hoje.month
    dia_atual = hoje.day
    dias_mes = dias_mes_data(hoje)

    metas = comercial.models.MetaFaturamento.objects.filter(
        data__year=ano_atual).order_by('data')
    if len(metas) == 0:
        return 'Nenhuma meta definida para o ano', None, None

    faturados = comercial.queries.faturamento_para_meta(
        cursor, ano_atual)
    for faturado in faturados:
        faturado['mes'] = int(faturado['mes'][:2])
    faturados_dict = {
        f['mes']: int(round(f['valor']/1000)) for f in faturados
    }

    devolvidos = comercial.queries.devolucao_para_meta.query(
        cursor, ano_atual)
    for devolvido in devolvidos:
        devolvido['mes'] = int(devolvido['mes'][:2])
    devolvidos_dict = {
        f['mes']: int(round(f['valor']/1000)) for f in devolvidos
    }

    pedidos = faturavel_modelo.pedido_faturavel_modelo(
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
        mes['faturamento'] = meta.faturamento
        mes['reparo'] = meta.reparo
        mes['planejado'] = meta.faturamento + meta.reparo
        mes['ajuste'] = meta.ajuste
        mes['imes'] = mes['mes'].month
        mes['faturado'] = (
            faturados_dict.get(mes['imes'], 0) -
            devolvidos_dict.get(mes['imes'], 0)
            )
        if mes['imes'] < mes_atual:
            if ano_atual < 2021:
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
                mes['acompensar'] = (
                    mes['faturado'] - mes['planejado'])
                total['acompensar'] += mes['acompensar'] + mes['ajuste']
                compensar += mes['planejado'] - mes['faturado'] - mes['ajuste']
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

    return None, meses, total
