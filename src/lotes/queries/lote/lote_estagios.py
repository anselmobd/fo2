from pprint import pprint

import lotes.queries


def get_estagios(cursor, lote):
    dados = lotes.queries.lote.posicao_so_estagios(cursor, lote[:4], lote[4:])
    return [
      row['COD_EST']
      for row in dados
    ]


def get_estagios_str(cursor, lote):
    estagios = get_estagios(cursor, lote)
    return list(map(str, estagios))
