from pprint import pprint

import lotes.queries


def query(cursor, lote):
    dados = lotes.queries.lote.posicao_so_estagios(cursor, lote[:4], lote[4:])
    return [
      row['COD_EST']
      for row in dados
    ]
