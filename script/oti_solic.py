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

def processa(lotes_sols):
    ls_sols = deepcopy(lotes_sols)
    for lote in ls_sols:
        info = ls_sols[lote]
        qtd_sol = sum(info[1].values())
        info[0] -= qtd_sol
        del info[1]
    return ls_sols


def get_lotes(lotes_sols):
    ls_sols = deepcopy(lotes_sols)
    for lote in ls_sols:
        del ls_sols[lote][1]
        ls_sols[lote] = ls_sols[lote][0]
    return ls_sols


def get_solicitacoes(lotes_sols):
    sols = {}
    for lote in lotes_sols:
        lote_sols = lotes_sols[lote][1]
        for sol in lote_sols:
            if sol not in sols:
                sols[sol] = 0
            sols[sol] += lote_sols[sol]
    return sols


def distribui_solicitacoes(lotes, solicitacoes):
    solic = {}
    lotes_items = sorted(lotes.items(), key=lambda x: x[1])
    sols_iter = iter(
        sorted(solicitacoes.items(), key=lambda x: x[1], reverse=True))
    qtd_sol = 0
    for lote, qtd_lote in lotes_items:
        solic[lote] = [qtd_lote, {}]
        while qtd_lote > 0:
            if qtd_sol == 0:
                try:
                    sol, qtd_sol = next(sols_iter)
                except StopIteration:
                    break
            qtd_deduzir = min(qtd_lote, qtd_sol)
            solic[lote][1][sol] = qtd_deduzir
            qtd_lote -= qtd_deduzir
            qtd_sol -= qtd_deduzir
    return solic


pprint(lotes_solicitados)
pprint(processa(lotes_solicitados))

lotes = get_lotes(lotes_solicitados)
pprint(lotes)
solicitacoes = get_solicitacoes(lotes_solicitados)
pprint(solicitacoes)

new_lotes_solicitados = distribui_solicitacoes(lotes, solicitacoes)
pprint(new_lotes_solicitados)
pprint(processa(new_lotes_solicitados))
