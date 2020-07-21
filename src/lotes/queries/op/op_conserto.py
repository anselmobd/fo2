from utils.functions.models import rows_to_dict_list


def op_conserto(cursor):
    sql = """
        SELECT
          lote.PROCONF_GRUPO REF
        , lote.PROCONF_ITEM COR
        , lote.PROCONF_SUBGRUPO TAM
        , lote.ORDEM_PRODUCAO OP
        , sum(lote.QTDE_CONSERTO ) QTD
        FROM PCPC_040 lote
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE lote.CODIGO_ESTAGIO <> 63
        GROUP BY
          lote.PROCONF_GRUPO
        , lote.PROCONF_ITEM
        , tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.ORDEM_PRODUCAO
        HAVING
          sum(lote.QTDE_CONSERTO ) > 0
        ORDER BY
          lote.PROCONF_GRUPO
        , lote.PROCONF_ITEM
        , tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.ORDEM_PRODUCAO
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
