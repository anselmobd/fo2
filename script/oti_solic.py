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
        lotes_sols[lote] = [qtd_lote, {}]
        while qtd_lote > 0:
            if qtd_sol == 0:
                try:
                    sol, qtd_sol = next(sols_iter)
                except StopIteration:
                    break
            qtd_deduzir = min(qtd_lote, qtd_sol)
            lotes_sols[lote][1][sol] = qtd_deduzir
            qtd_lote -= qtd_deduzir
            qtd_sol -= qtd_deduzir
    return lotes_sols


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


lotes_solicitados = lot_sol_dict(lotes_solicitados)

# pprint(lotes_solicitados)
pprint(processa(lotes_solicitados))

lotes = get_lotes(lotes_solicitados)
pprint(lotes)
solicitacoes = get_solicitacoes(lotes_solicitados)
pprint(solicitacoes)

# usar_lotes, nao_usar_lotes = separa_lotes(lotes, solicitacoes)
# pprint(usar_lotes)

# new_lotes_solicitados = distribui_solicitacoes(usar_lotes, solicitacoes)
# new_lotes_solicitados.update({lote: [qtd, {}] for lote, qtd in nao_usar_lotes.items()})

# pprint(new_lotes_solicitados)
# pprint(processa(new_lotes_solicitados))
