from fo2.models import rows_to_dict_list


def quant_estagio(cursor, estagio, ref, tipo):
    filtra_estagio = ''
    if estagio != '':
        filtra_estagio = """--
            AND l.CODIGO_ESTAGIO = {} """.format(estagio)

    filtra_ref = ''
    if ref != '':
        filtra_ref = """--
            AND l.PROCONF_GRUPO LIKE '{}' """.format(ref)

    filtro_tipo = ''
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

    sql = """
        SELECT
          l.CODIGO_ESTAGIO ESTAGIO
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , sum(
            CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum(l.QTDE_EM_PRODUCAO_PACOTE) QUANT
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem cofec. gerada
        --  AND l.PERIODO_PRODUCAO = 1921
        --  AND l.ORDEM_CONFECCAO = 01866
          {filtra_estagio} -- filtra_estagio
          {filtra_ref} -- filtra_ref
          {filtro_tipo} -- filtro_tipo
        GROUP BY
          l.CODIGO_ESTAGIO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        HAVING
          sum(l.QTDE_EM_PRODUCAO_PACOTE) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """.format(
        filtra_ref=filtra_ref,
        filtra_estagio=filtra_estagio,
        filtro_tipo=filtro_tipo,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def totais_estagios(cursor, tipo_roteiro, cnpj9):
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

    sql = """
        SELECT
          l.CODIGO_ESTAGIO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
            THEN
              l.QTDE_EM_PRODUCAO_PACOTE *
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
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
            THEN
              l.QTDE_EM_PRODUCAO_PACOTE *
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
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
            THEN
              l.QTDE_EM_PRODUCAO_PACOTE *
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
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.PROCONF_GRUPO NOT LIKE 'F%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.PROCONF_GRUPO NOT LIKE 'F%'
            THEN
              l.QTDE_EM_PRODUCAO_PACOTE *
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
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_MP
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'F%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_MP
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'F%'
            THEN
              l.QTDE_EM_PRODUCAO_PACOTE *
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
            CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum(l.QTDE_EM_PRODUCAO_PACOTE) QUANT
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE o.SITUACAO in (4, 2) -- Ordens em produção, Ordem cofec. gerada
        {filtro_tipo_roteiro} -- filtro_tipo_roteiro
        {filtro_cnpj9} -- filtro_cnpj9
        GROUP BY
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        HAVING
          sum(l.QTDE_EM_PRODUCAO_PACOTE) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
    """.format(
        filtro_tipo_roteiro=filtro_tipo_roteiro,
        filtro_cnpj9=filtro_cnpj9,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
