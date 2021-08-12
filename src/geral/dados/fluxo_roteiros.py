from pprint import pprint

from geral.dados.fluxos import dict_fluxo


def get_roteiros_de_fluxo(id):
    fluxo = dict_fluxo(id)

    roteiros = {}
    fluxo_num = fluxo['fluxo_num']
    for k in fluxo:
        if isinstance(fluxo[k], dict):
            if 'ests' in fluxo[k]:
                if k == 'bloco':
                    tipo = fluxo[k]['nivel']
                else:
                    tipo = k[:2]
                if tipo == 'mp':
                    tipo = 'md'
                if tipo not in roteiros:
                    roteiros[tipo] = {}
                roteiros[tipo][fluxo_num+fluxo[k]['alt_incr']] = [
                    fluxo[k]['ests'],
                    fluxo[k]['gargalo'],
                ]
    return roteiros
