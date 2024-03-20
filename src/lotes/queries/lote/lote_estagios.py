from pprint import pprint

import lotes.queries


def get_estagios(cursor, lote, colunas, cod_est_fn=None):
    dados = lotes.queries.lote.posicao_so_estagios(cursor, lote=lote)
    cod_est_fn = cod_est_fn if cod_est_fn else lambda x: x
    return [
        {
            col: cod_est_fn(row[col]) if col == 'COD_EST' else row[col]
            for col in colunas
        }
        for row in dados
    ]
