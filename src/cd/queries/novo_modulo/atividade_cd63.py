from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


__atividade = {
    1: "Colocando lote em palete",
    2: "Tirando lote de palete",
    3: "(Des)Endereçando palete",  # não utilizado em movimentos de lotes
}


__deposito = {
    101: "101-Atacado",
    102: "102-Varejo",
    231: "231-Interno",
}


def query(cursor, data_de, data_ate):

    sql = f"""
        SELECT
          trunc(h.DATA_HORA) DATA
        , h.USUARIO
        , op.DEPOSITO_ENTRADA DEP
        , h.ATIVIDADE
        , count(*) QTD
        FROM ENDR_016_HIST h -- histórico de endereçamento
        LEFT JOIN PCPC_020 op
          ON op.ORDEM_PRODUCAO = h.ORDEM_PRODUCAO
        WHERE 1=1
          AND h.DATA_HORA >= DATE '{data_de}'
          AND h.DATA_HORA <= DATE '{data_ate}'
        GROUP BY
          trunc(h.DATA_HORA)
        , h.USUARIO
        , op.DEPOSITO_ENTRADA
        , h.ATIVIDADE
        ORDER BY
          trunc(h.DATA_HORA)
        , h.USUARIO
        , op.DEPOSITO_ENTRADA
        , h.ATIVIDADE
    """
    debug_cursor_execute(cursor, sql)

    data = dictlist_lower(cursor)
    for row in data:
        row['atividade'] = __atividade[row['atividade']]
        row['dep'] = __deposito[row['dep']]
        row['data'] = row['data'].date()

    return data
