from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def query_colecao(cursor):
    sql = f'''
        SELECT
          col.COLECAO
        , col.DESCR_COLECAO
        , sum(
            CASE WHEN re.NIVEL_ESTRUTURA = 1 THEN 1 ELSE 0 END 
          ) PRODUTO
        , sum(
            CASE WHEN re.REFERENCIA < 'A0000'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) PA
        , sum(
            CASE WHEN re.REFERENCIA LIKE 'A%'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) PG
        , sum(
            CASE WHEN re.REFERENCIA LIKE 'B%'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) PB
        , sum(
            CASE WHEN re.REFERENCIA LIKE 'F%'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) PARTE
        , sum(
            CASE WHEN re.REFERENCIA > '99999'
                  AND NOT re.REFERENCIA LIKE 'F%' 
                  AND NOT re.REFERENCIA LIKE 'Z%'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) MD
        , sum(
            CASE WHEN re.REFERENCIA LIKE 'Z%'
                  AND re.NIVEL_ESTRUTURA = 1
            THEN 1 ELSE 0 END 
          ) MP
        , sum(
            CASE WHEN re.NIVEL_ESTRUTURA != 1 THEN 1 ELSE 0 END 
          ) INSUMO
        , count(re.REFERENCIA) TOTAL
        FROM BASI_140 col
        LEFT JOIN basi_030 re
          ON re.COLECAO = col.COLECAO 
        AND NOT re.DESCR_REFERENCIA LIKE '-%'
        GROUP BY
          col.COLECAO
        , col.DESCR_COLECAO
        ORDER BY
          col.COLECAO
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
