from pprint import pprint

from django.core.cache import cache

from utils.functions.models import dictlist

from utils.functions import my_make_key_cache, fo2logger
from utils.functions.queries import coalesce, sql_where, sql_where_none_if


def totais_estagios(
      cursor, tipo_roteiro, cnpj9, deposito, data_de, data_ate, ops_prog=[]):

    key_cache = my_make_key_cache(
        'totais_estagios', tipo_roteiro, cnpj9, deposito, data_de, data_ate, str(ops_prog))

    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtro_tipo_roteiro = ''
    if tipo_roteiro != 't':
        not_operation = 'NOT' if tipo_roteiro == 'p' else ''
        filtro_tipo_roteiro = f'''--
            AND {not_operation} EXISTS
              ( SELECT
                  ia.*
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP <= 'B9999'
              ) -- se tem componente que é PA, PG ou PB
        '''

    filtro_cnpj9 = sql_where('r.CGC_CLIENTE_9', cnpj9)

    filtro_deposito = sql_where_none_if(
        'o.DEPOSITO_ENTRADA', deposito, '', quote='')

    data_de = coalesce(data_de, '')
    filtro_data_de = sql_where_none_if(
        'o.DATA_ENTRADA_CORTE', str(data_de), '', operation=">=")

    data_ate = coalesce(data_ate, '')
    filtro_data_ate = sql_where_none_if(
        'o.DATA_ENTRADA_CORTE', str(data_ate), '', operation="<=")

    filtro_op_prog = sql_where(
        'l.ORDEM_PRODUCAO', tuple([0]+ops_prog), operation="IN")

    sql = f"""
        SELECT
          CASE WHEN e.DESCRICAO IS NULL THEN l.CODIGO_ESTAGIO+100
          ELSE l.CODIGO_ESTAGIO
          END CODIGO_ESTAGIO
        , l.CODIGO_ESTAGIO || ' - ' || 
          CASE WHEN e.DESCRICAO IS NULL THEN e_p.DESCRICAO 
          ELSE e.DESCRICAO 
          END ESTAGIO
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
              AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1 ELSE 0 END
          ) LOTES_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
            THEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)
            ELSE 0
            END
          ) QUANT_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
            THEN
              (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
              ( SELECT
                  CASE WHEN count(*) = 0 THEN 1
                  ELSE count(*) END
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP NOT IN 'F%'
              )
            ELSE 0
            END
          ) PECAS_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
              AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1 ELSE 0 END
          ) LOTES_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
            THEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)
            ELSE 0
            END
          ) QUANT_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
            THEN
              (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
              ( SELECT
                  CASE WHEN count(*) = 0 THEN 1
                  ELSE count(*) END
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP NOT IN 'F%'
              )
            ELSE 0
            END
          ) PECAS_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
              AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1 ELSE 0 END
          ) LOTES_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
            THEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)
            ELSE 0
            END
          ) QUANT_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
            THEN
              (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
              ( SELECT
                  CASE WHEN count(*) = 0 THEN 1
                  ELSE count(*) END
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP NOT IN 'F%'
              )
            ELSE 0
            END
          ) PECAS_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.PROCONF_GRUPO NOT LIKE 'F%'
              AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1 ELSE 0 END
          ) LOTES_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.PROCONF_GRUPO NOT LIKE 'F%'
            THEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)
            ELSE 0
            END
          ) QUANT_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.PROCONF_GRUPO NOT LIKE 'F%'
            THEN
              (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
              ( SELECT
                  CASE WHEN count(*) = 0 THEN 1
                  ELSE count(*) END
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP NOT IN 'F%'
              )
            ELSE 0
            END
          ) PECAS_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'F%'
              AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1 ELSE 0 END
          ) LOTES_MP
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'F%'
            THEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)
            ELSE 0
            END
          ) QUANT_MP
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'F%'
            THEN
              (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
              ( SELECT
                  CASE WHEN count(*) = 0 THEN 1
                  ELSE count(*) END
                FROM BASI_050 ia -- insumos de alternativa
                WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                  AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                  AND ia.NIVEL_COMP = 1
                  AND ia.GRUPO_COMP NOT IN 'F%'
              )
            ELSE 0
            END
          ) PECAS_MP
        , sum(
            CASE WHEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) QUANT
        , sum(
            (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) *
            ( SELECT
                CASE WHEN count(*) = 0 THEN 1
                ELSE count(*) END
              FROM BASI_050 ia -- insumos de alternativa
              WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
                AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
                AND ia.NIVEL_COMP = 1
                AND ia.GRUPO_COMP NOT IN 'F%'
            )
          ) PECAS
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        LEFT JOIN MQOP_005 e_p
          ON e_p.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
         {filtro_op_prog} -- filtro_op_prog
        LEFT JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        AND e_p.CODIGO_ESTAGIO IS NULL 
        WHERE o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
          {filtro_tipo_roteiro} -- filtro_tipo_roteiro
          {filtro_cnpj9} -- filtro_cnpj9
          {filtro_deposito} -- filtro_deposito
          {filtro_data_de} -- filtro_data_de
          {filtro_data_ate} -- filtro_data_ate
          AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
        GROUP BY
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        , e_p.DESCRICAO
        HAVING
          sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
    """
    cursor.execute(sql)

    cached_result = dictlist(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
