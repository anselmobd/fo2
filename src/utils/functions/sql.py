from pprint import pprint

from utils.functions.list import (
    count_at_end,
    count_at_start,
    empty,
)


__all__ = [
    'sql_formato_fo2',
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
