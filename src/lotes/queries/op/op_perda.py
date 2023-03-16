from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def op_perda(cursor, data_de, data_ate, detalhe):
    sql = """
        SELECT
          lote.PROCONF_GRUPO REF
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM COR
            , lote.PROCONF_SUBGRUPO TAM
        """
    sql += """
        , lote.ORDEM_PRODUCAO OP
        , sum(lote.QTDE_PERDAS ) QTD
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
              AND l.SEQUENCIA_ESTAGIO = 1
          ) QTDOP
        FROM PCPC_040 lote
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE o.DATA_ENTRADA_CORTE >= %s
          AND o.DATA_ENTRADA_CORTE <= %s
        GROUP BY
          lote.PROCONF_GRUPO
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM
            , tam.ORDEM_TAMANHO
            , lote.PROCONF_SUBGRUPO
        """
    sql += """
        , lote.ORDEM_PRODUCAO
        HAVING
          sum(lote.QTDE_PERDAS ) > 0
        ORDER BY
          lote.PROCONF_GRUPO
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM
            , tam.ORDEM_TAMANHO
            , lote.PROCONF_SUBGRUPO
        """
    sql += """
        , lote.ORDEM_PRODUCAO
    """
    debug_cursor_execute(cursor, sql, [data_de, data_ate])
    return dictlist(cursor)
