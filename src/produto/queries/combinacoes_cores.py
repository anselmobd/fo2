from utils.functions.models import rows_to_dict_list


def combinacoes_cores(cursor, ref, alt):
    # Detalhando Estruturas
    sql = """
        WITH
        item_cores AS 
        ( SELECT DISTINCT 
            i.NIVEL_ESTRUTURA
          , i.GRUPO_ESTRUTURA
          , i.ITEM_ESTRUTURA
          FROM BASI_010 i -- item
        )
        SELECT 
          e.ALTERNATIVA_ITEM ALT
        -- , e.SEQUENCIA
        --, e.NIVEL_ITEM 
        --, e.GRUPO_ITEM 
        --, e.SUB_ITEM 
        -- , e.ITEM_ITEM 
        --, e.NIVEL_COMP
        --, e.GRUPO_COMP
        --, e.SUB_COMP 
        -- , e.ITEM_COMP
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_ITEM
          ELSE icor.ITEM_ESTRUTURA
          END COR_ITEM
        , TRUNC(e.CONSUMO) CONSUMO
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE e.ITEM_COMP
          END COR_COMP
        --, e.*
        FROM BASI_050 e
        LEFT JOIN BASI_040 coc -- combinação cor
          ON e.ITEM_COMP = '000000'
        AND coc.SUB_ITEM = '000'
        AND coc.GRUPO_ITEM = e.GRUPO_ITEM
        AND coc.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
        AND coc.SEQUENCIA = e.SEQUENCIA
        LEFT JOIN item_cores icor -- cores por item 
          ON e.ITEM_COMP <> '000000'
        AND icor.NIVEL_ESTRUTURA = e.NIVEL_COMP
        AND icor.GRUPO_ESTRUTURA = e.GRUPO_COMP
        AND ( e.ITEM_ITEM = '000000'
            OR icor.ITEM_ESTRUTURA = e.ITEM_ITEM
            ) 
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE 1=1
          AND e.NIVEL_ITEM = 1
          AND e.GRUPO_ITEM = %s
          AND e.ALTERNATIVA_ITEM = %s
          AND e.NIVEL_COMP = 1
        ORDER BY
          e.ALTERNATIVA_ITEM
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_ITEM
          ELSE icor.ITEM_ESTRUTURA
          END
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE e.ITEM_COMP
          END
    """
    cursor.execute(sql, [ref, alt])
    return rows_to_dict_list(cursor)
