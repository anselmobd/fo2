from copy import deepcopy
from pprint import pprint


solicitacoes = {
    '#': 14,
    2807: 6,
    2856: 45,
    2861: 13,
    2864: 2,
    2876: 27,
    2923: 534,
    2980: 459,
    2981: 27,
    2999: 16,
}


lotes = {
    220304159: ('1Q0027', 100),
    230901615: ('1Q0042', 100),
    230901625: ('1Q0042', 100),
    231202127: ('1Q0043', 100),
    224802702: ('1Q0044', 13),
    231202132: ('1Q0044', 100),
    231801970: ('1Q0047', 48),
    231801975: ('1Q0047', 39),
    231202124: ('1Q0052', 100),
    231202125: ('1Q0052', 100),
    231202128: ('1Q0052', 100),
    231202129: ('1Q0052', 100),
    231202130: ('1Q0052', 100),
    231202131: ('1Q0052', 100),
    231202133: ('1Q0052', 100),
}

def ini_lote(value, sols):
    return {
        'end': value[0],
        'ini': value[1],
        'fim': None,
        'sols': sols,
    }


def quant_total(dict_quant):
    return sum(dict_quant.values())


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


def lotes_uma_sol(new_lotes_sols, sols):
    for value in new_lotes_sols.values():
        if value['fim'] is None:
            sols_iguais = [
                sol for sol, qtd in sols.items()
                if qtd == value['ini']
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
                if sols[sol] == 0:
                    del(sols[sol])
                    try:
                        sol = next(sols_iter)
                    except StopIteration:
                        break
                qtd_deduzir = min(value['fim'], sols[sol])
                value['sols'][sol] = qtd_deduzir
                value['fim'] -= qtd_deduzir
                sols[sol] -= qtd_deduzir
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


def keys_order_by_value(lotes):
    lotes_items = sorted(lotes.items(), key=lambda x: x[1], reverse=True)
    return list(map(lambda x: x[0], lotes_items))


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
    pprint(solicitacoes)

    print()
    print("Solicitações ordenadas para uso")
    sols_ord = keys_order_by_value(solicitacoes)
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
