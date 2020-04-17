from utils.functions.models import rows_to_dict_list


def os_inform(cursor, os):
    # Informações sobre OS
    return get_os(cursor, os=os)


def op_get_os(cursor, op):
    # Informações sobre OS
    return get_os(cursor, op=op)


def get_os(cursor, os='', op='', periodo='', oc=''):
    # Informações sobre OS

    filtro_os = ''
    filtro_op = ''
    filtro_periodo = ''
    filtro_oc = ''
    filtro_join = ''
    if os is not None and os != '':
        filtro_os = "AND os.NUMERO_ORDEM = '{}'".format(os)
    else:
        if op is not None and op != '':
            filtro_op = "AND l.ORDEM_PRODUCAO = '{}'".format(op)
        if periodo is not None and periodo != '':
            filtro_periodo = "AND l.PERIODO_PRODUCAO = '{}'".format(periodo)
        if oc is not None and oc != '':
            filtro_oc = "AND l.ORDEM_CONFECCAO = '{}'".format(oc)

        if filtro_op or filtro_periodo or filtro_oc:
            filtro_join = \
                'AND l.NUMERO_ORDEM IS NOT NULL AND l.NUMERO_ORDEM != 0'
    sql = """
        SELECT DISTINCT
          os.NUMERO_ORDEM OS
        , os.CODIGO_SERVICO || '-' || s.DESC_TERCEIRO SERV
        , os.CGCTERC_FORNE9 CNPJ9
        , os.CGCTERC_FORNE4 CNPJ4
        , os.CGCTERC_FORNE2 CNPJ2
        , f.NOME_FANTASIA NOME
        , CASE os.SITUACAO_ORDEM
          WHEN 1 THEN '1-Aberta'
          WHEN 2 THEN '2-Em Processo'
          WHEN 3 THEN '3-Baixa Parcial'
          WHEN 4 THEN '4-Baixa Total'
          ELSE '-'
          END SITUACAO
        , os.COD_CANC_ORDEM || '-' || c.DESCR_CANC_ORDEM CANC
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(
            CASE WHEN l.QTDE_A_PRODUZIR_PACOTE <> 0
            THEN l.QTDE_A_PRODUZIR_PACOTE
            ELSE --l.QTDE_PECAS_PROG
              QTDE_PECAS_PROD
            + QTDE_CONSERTO
            + QTDE_PECAS_2A
            + QTDE_PERDAS
            END
          ) QTD
        , os.DATA_EMISSAO
        , os.DATA_ENTREGA
        , os.OBSERVACAO
        FROM OBRF_080 os
        JOIN OBRF_070 s
          ON s.CODIGO_TERCEIRO = os.CODIGO_SERVICO
        JOIN SUPR_010 f
          ON f.FORNECEDOR9 = os.CGCTERC_FORNE9
         AND f.FORNECEDOR4 = os.CGCTERC_FORNE4
        JOIN OBRF_087 c
          ON c.COD_CANC_ORDEM = os.COD_CANC_ORDEM
        LEFT JOIN pcpc_040 l
          ON l.NUMERO_ORDEM = os.NUMERO_ORDEM
        WHERE 1=1
          {filtro_os} -- filtro_os
          {filtro_op} -- filtro_op
          {filtro_periodo} -- filtro_periodo
          {filtro_oc} -- filtro_oc
          {filtro_join} -- filtro_join
        GROUP BY
          os.NUMERO_ORDEM
        , os.CODIGO_SERVICO
        , s.DESC_TERCEIRO
        , os.CGCTERC_FORNE9
        , os.CGCTERC_FORNE4
        , os.CGCTERC_FORNE2
        , f.NOME_FANTASIA
        , os.SITUACAO_ORDEM
        , os.COD_CANC_ORDEM
        , c.DESCR_CANC_ORDEM
        , os.DATA_EMISSAO
        , os.DATA_ENTREGA
        , os.OBSERVACAO
        ORDER BY
          os.NUMERO_ORDEM
    """.format(
        filtro_os=filtro_os,
        filtro_op=filtro_op,
        filtro_periodo=filtro_periodo,
        filtro_oc=filtro_oc,
        filtro_join=filtro_join,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
