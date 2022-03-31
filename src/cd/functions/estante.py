from pprint import pprint

__all__ = ['gera_estantes_enderecos']


def gera_estantes_enderecos():
    estantes = {
        'A': {
            'len': 28,
        },
        'B': {
            'len': 28,
            'exclude': {
                (12, 13): (1,)
            }
        },
        'C': {
            'len': 28,
            'exclude': {
                (12, 13): (1,)
            }
        },
        'D': {
            'len': 28,
            'exclude': {
                (6, 13, 14, 22): (1, 2, 3)
            }
        },
        'E': {
            'len': 30,
            'exclude': {
                (13, 14): (1,)
            }
        },
        'F': {
            'len': 30,
            'exclude': {
                (12, 13): (1,)
            }
        },
        'G': {
            'len': 30,
            'exclude': {
                (12, 13): (1,)
            }
        },
        'H': {
            'len': 30,
        },
    }
    enderecos = []
    enderecos_excludes = []
    for estante in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        for coluna in range(estantes[estante]['len']):
            for andar in range(1, 4):
                try:
                    exclude = estantes[estante]['exclude']
                except KeyError:
                    exclude = {}
                try:
                    colunas_diferentes = list(exclude.keys())[0]
                except IndexError:
                    colunas_diferentes = []
                if coluna in colunas_diferentes:
                    try:
                        andares_excludes = list(exclude.values())[0]
                    except IndexError:
                        andares_excludes = []
                    andar_exclude = andar in andares_excludes
                else:
                    andar_exclude = False
                endereco = f"1{estante}{andar:02}{coluna:02}"
                if andar_exclude:
                    enderecos_excludes.append(endereco)
                else:
                    enderecos.append(endereco)
    return enderecos


def gera_quarto_andar_enderecos():
    return [
        f"1Q{i:04}"
        for i in range(1, 51)
    ]