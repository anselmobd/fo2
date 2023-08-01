from copy import deepcopy
from pprint import pprint

solicitacoes = {
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

def processa(solics):
    sols = deepcopy(solics)
    for lote in sols:
        info = sols[lote]
        qtd_sol = sum(info[1].values())
        info[0] -= qtd_sol
        del info[1]
    return sols


def get_lotes(solics):
    sols = deepcopy(solics)
    for lote in sols:
        del sols[lote][1]
        sols[lote] = sols[lote][0]
    return sols


def get_pedidos(solics):
    pedidos = {}
    for lote in solics:
        lote_peds = solics[lote][1]
        for ped in lote_peds:
            if ped not in pedidos:
                pedidos[ped] = 0
            pedidos[ped] += lote_peds[ped]
    return pedidos


def distribui_pedidos(lotes, pedidos):
    solic = {}
    lotes_items = sorted(lotes.items(), key=lambda x: x[1])
    pedidos_iter = iter(
        sorted(pedidos.items(), key=lambda x: x[1], reverse=True))
    qtd_pedido = 0
    for lote, qtd_lote in lotes_items:
        solic[lote] = [qtd_lote, {}]
        while qtd_lote > 0:
            if qtd_pedido == 0:
                try:
                    pedido, qtd_pedido = next(pedidos_iter)
                except StopIteration:
                    break
            qtd_deduzir = min(qtd_lote, qtd_pedido)
            solic[lote][1][pedido] = qtd_deduzir
            qtd_lote -= qtd_deduzir
            qtd_pedido -= qtd_deduzir
    return solic


pprint(solicitacoes)
pprint(processa(solicitacoes))

lotes = get_lotes(solicitacoes)
pprint(lotes)
pedidos = get_pedidos(solicitacoes)
pprint(pedidos)

new_solic = distribui_pedidos(lotes, pedidos)
pprint(new_solic)
pprint(processa(new_solic))
