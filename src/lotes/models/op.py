from utils.functions.models import (
    rows_to_dict_list,
    rows_to_dict_list_lower,
)

import lotes.queries.lote
import lotes.queries.os


def op_tam_cor_qtd(cursor, op):
    sql = """
        SELECT
          lote.PROCONF_SUBGRUPO TAM
        , lote.PROCONF_ITEM COR
        , sum(lote.QTDE_PECAS_PROG ) QTD
        FROM PCPC_040 lote
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE lote.ORDEM_PRODUCAO = %s
          AND lote.SEQUENCIA_ESTAGIO
              = COALESCE(
                  (
                    SELECT
                      MIN(ulote.SEQUENCIA_ESTAGIO)
                    FROM PCPC_040 ulote
                    WHERE ulote.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                      AND ulote.ORDEM_CONFECCAO = lote.ORDEM_CONFECCAO
                    GROUP BY
                      ulote.ORDEM_PRODUCAO
                    , ulote.ORDEM_CONFECCAO
                  )
                , 0)
        GROUP BY
          tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.PROCONF_ITEM
        ORDER BY
          tam.ORDEM_TAMANHO
        , lote.PROCONF_ITEM
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


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
            WHERE l.ORDEM_PRODUCAO = 9242
              AND l.SEQ_OPERACAO = (
                SELECT
                  MIN( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
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
    cursor.execute(sql, [data_de, data_ate])
    return rows_to_dict_list(cursor)


def busca_ops_info(cursor, ops):
    filtro_op = ''
    sep = '('
    for op in ops:
        filtro_op += "{} '{}'".format(sep, op)
        sep = ','

    sql = """
        SELECT
          op.ORDEM_PRODUCAO OP
        , op.PEDIDO_VENDA PEDIDO
        FROM PCPC_020 op -- OP capa
        WHERE op.ORDEM_PRODUCAO IN
        --( 12345
        --, 12334
        {filtro_op} -- filtro_op
        )
    """.format(
        filtro_op=filtro_op,
    )

    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
