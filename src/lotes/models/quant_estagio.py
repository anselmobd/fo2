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


def totais_estagios(cursor):
    sql = """
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
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
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_MD
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
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE o.SITUACAO in (4, 2) -- Ordens em produção, Ordem cofec. gerada
        GROUP BY
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        HAVING
          sum(l.QTDE_EM_PRODUCAO_PACOTE) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
