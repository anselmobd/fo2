from copy import deepcopy
from pprint import pprint


solicitacoes = {
    2836: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47050,
           'pedido_destino': 999001911,
           'qtde': 11,
           'situacao': 4,
           'sub_destino': 'P'},
    2856: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '00156',
           'oc_destino': 0,
           'op_destino': 47070,
           'pedido_destino': 999001931,
           'qtde': 19,
           'situacao': 4,
           'sub_destino': 'P'},
    2861: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47130,
           'pedido_destino': 999001951,
           'qtde': 14,
           'situacao': 4,
           'sub_destino': 'P'},
    2865: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47032,
           'pedido_destino': 38201,
           'qtde': 10,
           'situacao': 4,
           'sub_destino': 'P'},
    2960: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47369,
           'pedido_destino': 999002057,
           'qtde': 4,
           'situacao': 4,
           'sub_destino': 'P'},
    2979: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47396,
           'pedido_destino': 999002076,
           'qtde': 3,
           'situacao': 4,
           'sub_destino': 'P'},
    2981: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47430,
           'pedido_destino': 999002077,
           'qtde': 7,
           'situacao': 4,
           'sub_destino': 'P'},
    2999: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47457,
           'pedido_destino': 999002096,
           'qtde': 6,
           'situacao': 4,
           'sub_destino': 'P'},
    3002: {'alter_destino': 74,
           'cor_destino': '0000ME',
           'grupo_destino': '0156A',
           'oc_destino': 0,
           'op_destino': 47487,
           'pedido_destino': 999002097,
           'qtde': 6,
           'situacao': 4,
           'sub_destino': 'P'}
}


lotes = {
    '230901570': ('1Q0043', 100),
    '231801897': ('1Q0036', 20),
    '231801933': ('1Q0037', 10)
}


def ini_lote(value, sols):
    return {
        'end': value[0],
        'ini': value[1],
        'fim': None,
        'sols': sols,
    }


def quant_total(dict_quant):
    return sum((row['qtde'] for _, row in dict_quant.items()))


def quant_total_lotes(dict_quant):
    return sum([
        qtd
        for _, qtd in dict_quant.values()
    ])


def lotes_nao_usar(new_lotes_sols, lotes_ord, qtd_nao_sol):
    for lote in lotes_ord:
        if qtd_nao_sol >= new_lotes_sols[lote]['ini']:
            new_lotes_sols[lote]['fim'] = new_lotes_sols[lote]['ini']
            qtd_nao_sol -= new_lotes_sols[lote]['ini']
        else:
            break


def lotes_uma_sol(new_lotes_sols, sols):
    for value in new_lotes_sols.values():
        if value['fim'] is None:
            sols_iguais = [
                sol for sol, info in sols.items()
                if info['qtde'] == value['ini']
            ]
            if sols_iguais:
                sol = sols_iguais[0]
                value['fim'] = 0
                value['sols'].update({
                    sol: sols[sol],
                })
                del(sols[sol])


def lotes_parciais(new_lotes_sols, lotes_ord, sols_ord, sols):
    sols_iter = iter(sols_ord)
    sol = next(sols_iter)
    new_lotes_sols_iter_ord = []
    for lote in lotes_ord:
        value = new_lotes_sols[lote]
        if value['fim'] is None:
            value['fim'] = value['ini']
            while value['fim'] > 0:
                if sols[sol]['qtde'] == 0:
                    del(sols[sol])
                    try:
                        sol = next(sols_iter)
                    except StopIteration:
                        break
                qtd_deduzir = min(value['fim'], sols[sol]['qtde'])
                value['sols'][sol] = sols[sol].copy()
                value['sols'][sol]['qtde'] = qtd_deduzir
                value['fim'] -= qtd_deduzir
                sols[sol]['qtde'] -= qtd_deduzir
        new_lotes_sols_iter_ord.append((lote, value))
    return new_lotes_sols_iter_ord


def conta_zerados(lotes_sols_procs):
    return sum(
        value['fim'] == 0
        for value in lotes_sols_procs.values()
    )


def inicia_distribuicao(lotes):
    lotes_sols = {}
    for lote, value in lotes.items():
        lotes_sols[lote] = ini_lote(value, {})
    return lotes_sols


def get_sols_ord(lotes):
    lotes_items = sorted(
        lotes.items(),
        key=lambda k: k[1]['qtde'],
        reverse=True,
    )
    return [lote_item[0] for lote_item in lotes_items]


def keys_order_by_dict(lotes_sols, reverse=False):
    lotes_items = sorted(
        lotes_sols.items(),
        key=lambda k: k[1]['end'],
    )
    mult = -1 if reverse else 1
    lotes_items_2 = sorted(
        lotes_items,
        key=lambda k: mult * k[1]['ini'],
    )
    return [lote_item[0] for lote_item in lotes_items_2]


if __name__ == '__main__':

    print("Solicitações")
    pprint(solicitacoes)
    total_sols = quant_total(solicitacoes)
    print("Total solicitado", total_sols)

    print()
    print("Lotes")
    pprint(lotes)
    total_lotes = quant_total_lotes(lotes)
    print("Total dos lotes", total_lotes)

    qtd_nao_solicitada = total_lotes - total_sols
    print("Quant. não solicitada", qtd_nao_solicitada)

    print()
    print("Inicia nova distribuição")

    print()
    print("Distribuição vazia")
    new_lotes_sols =  inicia_distribuicao(lotes)
    pprint(new_lotes_sols)

    print()
    print("Lotes em ordem decrescente de quantidade")
    lotes_ord = keys_order_by_dict(new_lotes_sols, reverse=True)
    pprint(lotes_ord)

    print()
    print("Definindo quantidade final de lotes a não utilizar")
    lotes_nao_usar(new_lotes_sols, lotes_ord, qtd_nao_solicitada)
    pprint(new_lotes_sols)

    print()
    print("Lotes atendidos com uma solicitação")
    lotes_uma_sol(new_lotes_sols, solicitacoes)
    pprint(new_lotes_sols)
    pprint(solicitacoes.keys())

    print()
    print("Solicitações ordenadas para uso")
    sols_ord = get_sols_ord(solicitacoes)
    pprint(sols_ord)

    print()
    print("Lotes em ordem crescente de quantidade")
    lotes_ord.reverse()
    pprint(lotes_ord)

    print()
    print("Empenhar demais lotes")
    new_lotes_sols_iter_ord = lotes_parciais(
        new_lotes_sols, lotes_ord, sols_ord, solicitacoes)
    pprint(new_lotes_sols)
    print(conta_zerados(new_lotes_sols), "lotes zerados")

    print()
    print("Visão ordenada dos empenhos otimizados")
    pprint(new_lotes_sols_iter_ord)
