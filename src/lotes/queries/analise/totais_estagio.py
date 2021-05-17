from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list

from utils.functions import my_make_key_cache, fo2logger


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
        if tipo_roteiro == 'p':
            filtro_tipo_roteiro += 'AND NOT EXISTS'
        else:
            filtro_tipo_roteiro += 'AND EXISTS'
        filtro_tipo_roteiro += '''
          ( SELECT
              ia.*
            FROM BASI_050 ia -- insumos de alternativa
            WHERE ia.GRUPO_ITEM = o.REFERENCIA_PECA
              AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
              AND ia.NIVEL_COMP = 1
              AND ia.GRUPO_COMP <= 'B9999'
          ) -- se tem componente que é PA, PG ou PB
        '''

    filtro_cnpj9 = ''
    if cnpj9 is not None:
        filtro_cnpj9 = '''--
            AND r.CGC_CLIENTE_9 = {}'''.format(cnpj9)

    filtro_deposito = ''
    if deposito is not None and deposito != '':
        filtro_deposito = '''--
            AND o.DEPOSITO_ENTRADA = {}'''.format(deposito)

    filtro_data_de = ''
    if data_de is not None and data_de != '':
        filtro_data_de = ''' --
            AND o.DATA_ENTRADA_CORTE >= '{}' '''.format(data_de)

    filtro_data_ate = ''
    if data_ate is not None and data_ate != '':
        filtro_data_ate = ''' --
            AND o.DATA_ENTRADA_CORTE <= '{}' '''.format(data_ate)

    sql = """
        SELECT
          l.CODIGO_ESTAGIO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
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
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
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
        HAVING
          sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
    """.format(
        filtro_tipo_roteiro=filtro_tipo_roteiro,
        filtro_cnpj9=filtro_cnpj9,
        filtro_deposito=filtro_deposito,
        filtro_data_de=filtro_data_de,
        filtro_data_ate=filtro_data_ate,
    )
    cursor.execute(sql)

    cached_result = rows_to_dict_list(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
