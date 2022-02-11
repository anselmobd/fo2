from pprint import pprint

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import debug_cursor_execute


def combinacoes_cores(cursor, ref, alt):
    # Detalhando Estruturas
    sql = f"""
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
        , CASE WHEN e.ITEM_ITEM = '000000' AND e.ITEM_COMP = '000000'
            THEN coc.ITEM_ITEM
          WHEN e.ITEM_ITEM <> '000000'
            THEN e.ITEM_ITEM
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
          ON e.ITEM_ITEM = '000000' AND e.ITEM_COMP <> '000000'
         AND icor.NIVEL_ESTRUTURA = e.NIVEL_ITEM 
         AND icor.GRUPO_ESTRUTURA = e.GRUPO_ITEM
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE 1=1
          AND e.NIVEL_ITEM = 1
          AND e.GRUPO_ITEM = '{ref}'
          AND e.ALTERNATIVA_ITEM = {alt}
          AND e.NIVEL_COMP = 1
        ORDER BY
          e.ALTERNATIVA_ITEM
        , CASE WHEN e.ITEM_ITEM = '000000' AND e.ITEM_COMP = '000000'
            THEN coc.ITEM_ITEM
          WHEN e.ITEM_ITEM <> '000000'
            THEN e.ITEM_ITEM
          ELSE icor.ITEM_ESTRUTURA
          END
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE e.ITEM_COMP
          END
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list(cursor)


def dict_combinacoes_cores(cursor, ref, alt):
    estrutura = combinacoes_cores(cursor, ref, alt)

    alt_cores = {}
    for row in estrutura:
        cor_item = row['COR_ITEM'].lstrip("0")
        cor_comp = row['COR_COMP'].lstrip("0")
        try:
            alt_cor = alt_cores[cor_item]
        except KeyError:
            alt_cores[cor_item] = {}
            alt_cor = alt_cores[cor_item]
        try:
            alt_cor[cor_comp] += row['CONSUMO']
        except KeyError:
            alt_cor[cor_comp] = row['CONSUMO']

    return alt_cores
