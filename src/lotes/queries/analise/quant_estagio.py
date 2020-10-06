from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list

from utils.functions import my_make_key_cache, fo2logger


def quant_estagio(
        cursor, estagio=None, ref=None, tipo=None, cor=None, tam=None,
        only=None, less=None, group=None, deposito=None):

    def monta_filtro(in_, estagios):
        filtro = ''
        if estagios is not None:
            lista_estagios = ''
            sep = ''
            for estagio in estagios:
                    lista_estagios += f'{sep}{str(estagio)}'
                    sep = ', '
            filtro = (
                f'AND l.CODIGO_ESTAGIO {in_} ({lista_estagios})')
        return filtro

    filtra_estagios = ' '.join([
        monta_filtro('IN', only),
        monta_filtro('NOT IN', less),
    ])

    filtra_estagio = ''
    if estagio is not None and estagio != '':
        filtra_estagio = """--
            AND l.CODIGO_ESTAGIO = {} """.format(estagio)

    filtra_ref = ''
    if ref is not None and ref != '':
        if '%' in ref:
            filtra_ref = """--
                AND l.PROCONF_GRUPO LIKE '{}' """.format(ref)
        else:
            filtra_ref = """--
                AND l.PROCONF_GRUPO = '{}' """.format(ref)

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = "AND l.PROCONF_SUBGRUPO = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = "AND l.PROCONF_ITEM = '{cor}'".format(cor=cor)

    filtro_deposito = ''
    if deposito is not None:
        filtro_deposito = f"AND o.DEPOSITO_ENTRADA = {deposito}"

    filtro_group = ''
    if group is not None:
        if group == 'o':
            filtro_group = ", o.ORDEM_PRODUCAO"
        elif group == 'op':
            filtro_group = """--
                , o.ORDEM_PRODUCAO
                , o.PEDIDO_VENDA"""

    filtro_tipo = ''
    if tipo is not None:
        if tipo == 'a':
            filtro_tipo = "AND l.PROCONF_GRUPO < 'A0000'"
        elif tipo == 'g':
            filtro_tipo = "AND l.PROCONF_GRUPO like 'A%'"
        elif tipo == 'b':
            filtro_tipo = "AND l.PROCONF_GRUPO like 'B%'"
        elif tipo == 'p':
            filtro_tipo = \
                "AND (l.PROCONF_GRUPO like 'A%' OR l.PROCONF_GRUPO like 'B%')"
        elif tipo == 'v':
            filtro_tipo = "AND l.PROCONF_GRUPO < 'C0000'"
        elif tipo == 'm':
            filtro_tipo = "AND l.PROCONF_GRUPO >= 'C0000'"

    sql = f"""
        SELECT
          sum(
            CASE WHEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) QUANT
        {filtro_group} -- filtro_group
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
          {filtro_deposito} -- filtro_deposito
        --  AND l.PERIODO_PRODUCAO = 1921
        --  AND l.ORDEM_CONFECCAO = 01866
          {filtra_estagio} -- filtra_estagio
          {filtra_estagios} -- filtra_estagios
          {filtra_ref} -- filtra_ref
          {filtro_tipo} -- filtro_tipo
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
        GROUP BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        HAVING
          sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) > 0
        ORDER BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def totais_estagios(cursor, tipo_roteiro, cnpj9, deposito, data_de, data_ate):
    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'totais_estagios', tipo_roteiro, cnpj9, deposito, data_de, data_ate)

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
