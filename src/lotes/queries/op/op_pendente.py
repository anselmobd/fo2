from utils.functions.models import rows_to_dict_list


def op_pendente(cursor, estagio, periodo_de, periodo_ate, data_de, data_ate,
                colecao, situacao, tipo):


    filtro_colecao = ''
    if colecao is not None and colecao != '':
        filtro_colecao = f"AND c.COLECAO = {colecao}"

    filtro_estagio = ''
    if estagio is not None and estagio != '':
        filtro_estagio = f"AND e.CODIGO_ESTAGIO = {estagio}"

    filtro_periodo_de = ''
    if periodo_de is not None and periodo_de != '':
        filtro_periodo_de = f"AND l.PERIODO_PRODUCAO >= {periodo_de}"

    filtro_periodo_ate = ''
    if periodo_ate is not None and periodo_ate != '':
        filtro_periodo_ate = f"AND l.PERIODO_PRODUCAO <= {periodo_ate}"

    filtro_data_de = ''
    if data_de is not None and data_de != '':
        filtro_data_de = f"AND o.DATA_ENTRADA_CORTE >= '{data_de}'"

    filtro_data_ate = ''
    if data_ate is not None and data_ate != '':
        filtro_data_ate = f"AND o.DATA_ENTRADA_CORTE <= '{data_ate}'"

    filtro_situacao = ''
    if situacao is not None and situacao != '':
        filtro_situacao = f"AND o.SITUACAO = {situacao}"

    filtro_tipo = ''
    if tipo == 'a':
        filtro_tipo = "AND l.PROCONF_GRUPO < 'A0000'"
    elif tipo == 'g':
        filtro_tipo = ("AND l.PROCONF_GRUPO >= 'A0000' "
                       "AND l.PROCONF_GRUPO < 'B0000'")
    elif tipo == 'b':
        filtro_tipo = ("AND l.PROCONF_GRUPO >= 'B0000' "
                       "AND l.PROCONF_GRUPO < 'C0000'")
    elif tipo == 'p':
        filtro_tipo = ("AND l.PROCONF_GRUPO >= 'A0000' "
                       "AND l.PROCONF_GRUPO < 'C0000'")
    elif tipo == 'v':
        filtro_tipo = "AND l.PROCONF_GRUPO < 'C0000'"
    elif tipo == 'm':
        filtro_tipo = "AND l.PROCONF_GRUPO >= 'C0000'"

    sql = f"""
        SELECT
          pend.*
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.SEQ_OPERACAO < pend.SEQ
            AND ll.QTDE_EM_PRODUCAO_PACOTE <> 0
          ) LOTES_ANTES
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.CODIGO_ESTAGIO = pend.CODIGO_ESTAGIO
          ) QTD_LOTES
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.SEQ_OPERACAO > pend.SEQ
            AND ll.QTDE_EM_PRODUCAO_PACOTE <> 0
          ) LOTES_DEPOIS
        FROM
        (
        SELECT
          e.CODIGO_ESTAGIO
        , e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , l.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO DATA_INI
        , p.DATA_FIM_PERIODO DATA_FIM
        , r.COLECAO || ' - ' || c.DESCR_COLECAO COLECAO
        , l.PROCONF_GRUPO REF
        , l.ORDEM_PRODUCAO OP
        , l.SEQ_OPERACAO SEQ
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.SITUACAO
        , SUM(l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) QTD
        , COUNT(*) LOTES
        FROM MQOP_005 e
        JOIN PCPC_040 l
          ON l.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
        JOIN BASI_030 r -- cadastro de produtos
          ON r.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND r.REFERENCIA = l.PROCONF_GRUPO
        JOIN BASI_140 c -- cadastro de coleções de produtos
          ON c.COLECAO = r.COLECAO
         {filtro_colecao} -- filtro_colecao
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
        WHERE (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) <> 0
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
          AND o.COD_CANCELAMENTO = 0 -- não cancelada
          {filtro_estagio} -- filtro_estagio
          {filtro_periodo_de} -- filtro_periodo_de
          {filtro_periodo_ate} -- filtro_periodo_ate
          {filtro_data_de} -- filtro_data_de
          {filtro_data_ate} -- filtro_data_ate
          {filtro_situacao} -- filtro_situacao
          {filtro_tipo} -- filtro_tipo
        GROUP BY
          e.CODIGO_ESTAGIO
        , e.DESCRICAO
        , l.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , l.PROCONF_GRUPO
        , r.COLECAO
        , c.DESCR_COLECAO
        , l.ORDEM_PRODUCAO
        , l.SEQ_OPERACAO
        , o.DATA_ENTRADA_CORTE
        , o.SITUACAO
        ORDER BY
          o.SITUACAO
        , e.CODIGO_ESTAGIO
        , l.PERIODO_PRODUCAO
        , r.COLECAO
        , l.PROCONF_GRUPO
        , l.ORDEM_PRODUCAO
        ) pend
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
