from copy import deepcopy
from pprint import pprint

lotes_solicitados = {
    223401575: [
        56,
        {
            2861: 35,  # 26,
        }
    ],
    223401576: [
        90,
        {
            2960: 3,
            2979: 9,
        }
    ],
    223204731: [
        35,
        {
            2960: 3,
            2979: 3,
            2981: 21,  # 21,
        }
    ],
    223204735: [
        47,
        {
            2836: 19,
            2856: 28,
        }
    ],
    223204737: [
        52,
        {
            2836: 19,  # 28,
            2856: 13,
            2937: 3,
        }
    ],
}


def ini_lote(qtd, sols):
    return {
        'ini': qtd,
        'fim': None,
        'sols': sols,
    }


def lot_sol_mount(lotes_solicitados):
    lotes_sols = {}
    for lote, value in lotes_solicitados.items():
        lotes_sols[lote] = ini_lote(*value)
        value = lotes_sols[lote]
        qtd_sol = sum(value['sols'].values())
        value['fim'] = value['ini'] - qtd_sol
    return lotes_sols


def get_lotes(lotes_solicitados):
    lotes = {}
    for lote, value in lotes_solicitados.items():
        lotes[lote] = value['ini']
    return lotes


def get_solicitacoes(lotes_solicitados):
    sols = {}
    for value in lotes_solicitados.values():
        for sol, qtd in value['sols'].items():
            if sol not in sols:
                sols[sol] = 0
            sols[sol] += qtd
    return sols


def quant_total(dict_quant):
    return sum(dict_quant.values())


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


print("Original")
lotes_solicitados = lot_sol_mount(lotes_solicitados)
pprint(lotes_solicitados)
print(conta_zerados(lotes_solicitados), "lotes zerados")

print()
print("Separando lotes e solicitações")

solicitacoes = get_solicitacoes(lotes_solicitados)
pprint(solicitacoes)
total_sols = quant_total(solicitacoes)
print("Total solicitado", total_sols)

lotes = get_lotes(lotes_solicitados)
pprint(lotes)
total_lotes = quant_total(lotes)
print("Total dos lotes", total_lotes)
qtd_nao_solicitada = total_lotes - total_sols
print("Quant. não solicitada", qtd_nao_solicitada)

print()
print("Inicia nova distribuição")

print()
print("Lotes ordenados para uso")
lotes_ord = keys_order_by_value(lotes)
pprint(lotes_ord)

print()
print("Distribuição vazia")
new_lotes_sols =  inicia_distribuicao(lotes)
pprint(new_lotes_sols)

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
print("Demais lotes do maior para o menor")
lotes_parciais(new_lotes_sols, lotes_ord, sols_ord, solicitacoes)
pprint(new_lotes_sols)
print(conta_zerados(new_lotes_sols), "lotes zerados")
