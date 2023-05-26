from itertools import cycle
from pprint import pprint

from utils.functions.list import (
    count_at_end,
    count_at_start,
    empty,
)


__all__ = [
    'sql_formato_fo2',
    'sql_quoted',
    'sql_test_in',
]


def sql_formato_fo2(sql):
    """Recebe um SQL como executado no RDBMS
    Retira a identação de todas as linhas não comentário e elimina
    linhas vazias do início e do final.
    Retorna SQL 'formatado'
    """
    linhas = sql.split('\n')

    min_spaces = 1000
    def strip_min_spaces(linha):
        nonlocal min_spaces
        linha_strip = linha.strip()
        if len(linha_strip) >= 2 and linha_strip[:2] != '--':
            min_spaces = min(
                min_spaces,
                count_at_start(linha, ' '),
            )
        return linha_strip

    linhas_strip = list(map(strip_min_spaces, linhas))

    linhas_vazias_inicio = count_at_start(linhas_strip, empty)
    linhas_vazias_final = count_at_end(linhas_strip, empty)

    del linhas[:linhas_vazias_inicio]
    if linhas_vazias_final:
        del linhas[-linhas_vazias_final:]

    def put_min_spaces(linha):
        nonlocal min_spaces
        linha_strip = linha.strip()
        if len(linha_strip) >= 2 and linha_strip[:2] != '--':
            linha = linha[min_spaces:]
        else:
            if len(linha_strip) >= 2:
                spaces = count_at_start(linha, ' ')
                linha = ' '*max(0, spaces-min_spaces)+linha_strip
            else:
                linha = linha_strip
        return linha

    linhas = list(map(put_min_spaces, linhas))
    return '\n'.join(linhas)


def sql_quoted(value, quotes="'"):
    quote = cycle(quotes)
    return f"{next(quote)}{value}{next(quote)}"


def sql_test_in(field, values, ligacao_condicional='AND'):
    if not values:
        return ''
    size = 999  # um a menos que 1000 apenas por margem de segurança
    lists = []
    for chunk in range(((len(values)-1) // size) + 1):
        lists.append(
            ", ".join([
                f"{sql_quoted(item)}"
                for item in values[chunk*size:chunk*size+size]
            ])
        )
    test = f"\nOR ".join([
        f"{field} IN ({list1})"
        for list1 in lists
    ])
    return f"{ligacao_condicional} ({test})"
