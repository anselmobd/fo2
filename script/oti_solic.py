from copy import deepcopy
from pprint import pprint

lotes_solicitados = {
    223401575: [
        56,
        {
            2861: 26,
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
            2981: 20,  # 21,
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
            2836: 28,
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


def lot_sol_dict(lotes_solicitados):
    lotes_sols = {}
    for lote, value in lotes_solicitados.items():
        lotes_sols[lote] = ini_lote(*value)
    return lotes_sols


def processa(lotes_solicitados):
    lotes_sols = deepcopy(lotes_solicitados)
    for value in lotes_sols.values():
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


def distribui_solicitacoes(lotes, solicitacoes):
    lotes_sols = {}
    lotes_items = sorted(lotes.items(), key=lambda x: x[1], reverse=True)
    sols_iter = iter(
        sorted(solicitacoes.items(), key=lambda x: x[1], reverse=True))
    qtd_sol = 0
    for lote, qtd_lote in lotes_items:
        lotes_sols[lote] = ini_lote(qtd_lote, {})
        while qtd_lote > 0:
            if qtd_sol == 0:
                try:
                    sol, qtd_sol = next(sols_iter)
                except StopIteration:
                    break
            qtd_deduzir = min(qtd_lote, qtd_sol)
            lotes_sols[lote]['sols'][sol] = qtd_deduzir
            qtd_lote -= qtd_deduzir
            qtd_sol -= qtd_deduzir
    return lotes_sols


def quant_total(dict_quant):
    return sum(dict_quant.values())


def separa_lotes(lotes, solicitacoes):
    qtd_sol = sum(solicitacoes.values())
    qtd_lotes = sum(lotes.values())
    qtd_fica = qtd_lotes - qtd_sol
    lotes_items = sorted(lotes.items(), key=lambda x: x[1], reverse=True)
    usar = {}
    nao_usar = {}
    for lote, qtd_lote in lotes_items:
        if qtd_fica >= qtd_lote:
            qtd_fica -= qtd_lote
            nao_usar[lote] = qtd_lote
        else:
            usar[lote] = qtd_lote
    return usar, nao_usar


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


lotes_solicitados = lot_sol_dict(lotes_solicitados)

print("Original")
lotes_sols_procs = processa(lotes_solicitados)
pprint(lotes_sols_procs)
print(conta_zerados(lotes_sols_procs), "lotes zerados")

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

print("Lotes ordenados para uso")
lotes_ord = keys_order_by_value(lotes)
pprint(lotes_ord)

print("Distribuição vazia")
new_lotes_sols =  inicia_distribuicao(lotes)
pprint(new_lotes_sols)

print("Definindo quantidade final de lotes a não utilizar")
lotes_nao_usar(new_lotes_sols, lotes_ord, qtd_nao_solicitada)
pprint(new_lotes_sols)

print("Lotes atendidos com uma solicitação")
lotes_uma_sol(new_lotes_sols, solicitacoes)
pprint(new_lotes_sols)
pprint(solicitacoes)

print("Solicitações ordenadas para uso")
sols_ord = keys_order_by_value(solicitacoes)
pprint(sols_ord)

print()
print("Separando lotes a usar e não usar")
usar_lotes, nao_usar_lotes = separa_lotes(lotes, solicitacoes)
pprint(usar_lotes)
pprint(nao_usar_lotes)

print()
print("Proposta")
new_lotes_solicitados = distribui_solicitacoes(usar_lotes, solicitacoes)
new_lotes_solicitados.update({lote: ini_lote(qtd, {}) for lote, qtd in nao_usar_lotes.items()})
lotes_sols_procs = processa(new_lotes_solicitados)
pprint(lotes_sols_procs)
print(conta_zerados(lotes_sols_procs), "lotes zerados")
