from utils.functions.models import rows_to_dict_list, dict_list_to_lower


def op_lotes2(cursor, op):
    sql = f'''
        WITH
        filtro AS (
        SELECT 
          {op} OP
        FROM dual
        ),
        ocs AS (
          SELECT DISTINCT 
            l.PERIODO_PRODUCAO PER
          , l.ORDEM_CONFECCAO OC
          , min(
              CASE
              WHEN l.QTDE_DISPONIVEL_BAIXA > 0
                OR l.QTDE_CONSERTO > 0
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END
            ) EST
          , min(
              CASE
              WHEN l.NUMERO_ORDEM > 0
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END
            ) EST_OS
          , max(l.NUMERO_ORDEM) OS
          FROM filtro f
          JOIN PCPC_040 l
            ON l.ORDEM_PRODUCAO = f.OP
          GROUP BY 
            l.PERIODO_PRODUCAO
          , l.ORDEM_CONFECCAO
        ),
        lotes AS (
          SELECT 
            ocs.EST
          , ed.DESCRICAO EST_DESCR
          , ocs.OS
          , ocs.EST_OS
          , eod.DESCRICAO EST_OS_DESCR
          , l.PROCONF_GRUPO REF
          , l.PROCONF_ITEM COR
          , l.PROCONF_SUBGRUPO TAM
          , t.ORDEM_TAMANHO TAM_ORD
          , ocs.PER
          , ocs.OC
          , l.QTDE_PECAS_PROG QTD
          FROM ocs
          JOIN PCPC_040 l
            ON l.PERIODO_PRODUCAO = ocs.PER 
          AND l.ORDEM_CONFECCAO = ocs.OC
          AND l.CODIGO_ESTAGIO = ocs.EST
          LEFT JOIN BASI_220 t
            ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
          JOIN MQOP_005 ed
            ON ed.CODIGO_ESTAGIO = ocs.EST
          LEFT JOIN MQOP_005 eod
            ON eod.CODIGO_ESTAGIO = ocs.EST_OS
        )
        SELECT
          l.EST || ' - ' || l.EST_DESCR EST
        , l.OS || ' (' || l.EST_OS_DESCR || ')' OS
        , l.REF
        , l.COR
        , l.TAM
        , l.PER PERIODO
        , l.OC
        , l.QTD
        FROM lotes l
        ORDER BY 
          l.EST
        , l.OS
        , l.REF
        , l.COR
        , l.TAM_ORD
        , l.PER
        , l.OC
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)

def op_lotes(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, op=op, order='e')


def os_lotes(cursor, os):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, os=os)


def get_imprime_lotes(cursor, op='', tam='', cor='', order='',
                      oc_ini='', oc_fim='', pula=None, qtd_lotes=None):
    # get dados de lotes
    data = get_lotes(
        cursor, op=op, tam=tam, cor=cor, order=order,
        oc_ini=oc_ini, oc_fim=oc_fim, pula=pula, qtd_lotes=qtd_lotes)
    data = dict_list_to_lower(data)
    return data


def get_lotes(cursor, op='', os='', tam='', cor='', order='',
              oc_ini='', oc_fim='', pula=None, qtd_lotes=None, oc=''):
    # Lotes
    if oc != '':
        oc_ini = oc
        oc_fim = oc
    if pula is None:
        pula = 0

    filtra_op = ''
    if op is not None and op != '':
      filtra_op = f'''--
          AND os.ORDEM_PRODUCAO = '{op}'
      '''

    filtra_os = ''
    if os is not None and os != '':
      filtra_os = f'''--
          AND os.NUMERO_ORDEM = '{os}'
      '''

    filtra_oc_ini = ''
    if oc_ini is not None and oc_ini != '':
      filtra_oc_ini = f'''--
          AND os.ORDEM_CONFECCAO >= '{oc_ini}'
      '''

    filtra_oc_fim = ''
    if oc_fim is not None and oc_fim != '':
      filtra_oc_fim = f'''--
          AND os.ORDEM_CONFECCAO <= '{oc_fim}'
      '''

    filtra_tam = ''
    if tam is not None and tam != '':
      filtra_tam = f'''--
          AND os.PROCONF_SUBGRUPO = '{tam}'
      '''

    filtra_cor = ''
    if cor is not None and cor != '':
      filtra_cor = f'''--
          AND os.PROCONF_ITEM = '{cor}'
      '''

    sql_pre_qtd_lotes = ''
    sql_pos_qtd_lotes = ''
    if qtd_lotes is not None:
        qtd_rows = pula + qtd_lotes
        sql_pre_qtd_lotes = 'WITH Table_qtd_lotes AS ('
        sql_pos_qtd_lotes = """)
            select * from Table_qtd_lotes where rownum <= {}""".format(
                qtd_rows)

    # order by
    if order == 'o':  # OC
        sql_order = '''ORDER BY
              l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO'''
    elif order == 't':  # OS + referência + tamanho + cor + OC
        sql_order = '''ORDER BY
              l.ORDEM_PRODUCAO
            , l.NUMERO_ORDEM
            , l.PROCONF_GRUPO
            , t.ORDEM_TAMANHO
            , l.PROCONF_ITEM
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO'''
    elif order == 'e':  # estágio + OS + referência + cor + tamanho + OC
        sql_order = '''ORDER BY
              1
            , l.ORDEM_PRODUCAO
            , l.NUMERO_ORDEM
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO'''
    elif order == 'r':  # referência + cor + tamanho + OC
        sql_order = '''ORDER BY
              l.ORDEM_PRODUCAO
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO'''
    elif order == 'w':  # referência + cor + tamanho + ROWID
        sql_order = '''ORDER BY
              l.ORDEM_PRODUCAO
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.ROW_ID'''
    else:  # elif order == '':  # OS + referência + cor + tamanho + OC
        sql_order = '''ORDER BY
              l.ORDEM_PRODUCAO
            , l.NUMERO_ORDEM
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO'''

    sql = f'''
        {sql_pre_qtd_lotes} -- sql_pre_qtd_lotes
        SELECT
          COALESCE(
          ( SELECT
              MIN( le.CODIGO_ESTAGIO ) CODIGO_ESTAGIO
            FROM PCPC_040 le
            JOIN MQOP_005 ed
              ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
            WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
              AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
              AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
          )
          , 9999
          ) EST_NUM
        , l.ORDEM_PRODUCAO OP
        , op.SITUACAO OP_SITUACAO
        , CASE WHEN dos.NUMERO_ORDEM IS NULL
          THEN '0'
          ELSE l.NUMERO_ORDEM || ' (' || eos.DESCRICAO || ')'
          END OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM COR
        , COALESCE(
            ( SELECT
                LISTAGG(le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO, ' & ')
                WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
              FROM PCPC_040 le
              JOIN MQOP_005 ed
                ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
              WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                --AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                AND le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO <> 0
            )
          , 'FINALIZADO'
          ) EST
        , COALESCE(
            ( SELECT
                LISTAGG(le.QTDE_EM_PRODUCAO_PACOTE, ';')
                WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
              FROM PCPC_040 le
              JOIN MQOP_005 ed
                ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
              WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
            )
          , ' '
          ) QUANTS
        , l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        , ( SELECT
              count(*)
            FROM (
              SELECT DISTINCT
                l_n.PERIODO_PRODUCAO
              , l_n.ORDEM_CONFECCAO
              , l_n.ORDEM_PRODUCAO
              FROM PCPC_040 l_n
            ) l_nn
            WHERE l_nn.PERIODO_PRODUCAO <= l.PERIODO_PRODUCAO
              AND l_nn.ORDEM_CONFECCAO <= l.ORDEM_CONFECCAO
              AND l_nn.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          ) NLOTE
        , ( SELECT
              count(*)
            FROM (
              SELECT DISTINCT
                l_t.PERIODO_PRODUCAO
              , l_t.ORDEM_CONFECCAO
              , l_t.ORDEM_PRODUCAO
              FROM PCPC_040 l_t
            ) l_tt
            WHERE l_tt.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          ) TOTLOTES
        , l.QTDE_PECAS_PROG QTD
        , l.QTDE_PECAS_PROD PROD1Q
        , l.QTDE_CONSERTO CONSERTO
        , l.QTDE_PECAS_2A PROD2Q
        , l.QTDE_PERDAS PERDA
        , r.NARRATIVA
        , ref.DESCR_REFERENCIA
        , tam.DESCR_TAM_REFER DESCR_TAMANHO
        , r.DESCRICAO_15 DESCR_COR
        , ref.COLECAO
        , CASE WHEN l.DIVISAO = 0 THEN dp.DIVISAO_PRODUCAO
          ELSE l.DIVISAO END DIVISAO
        , CASE WHEN l.DIVISAO = 0 THEN dp.DESCRICAO
          ELSE di.DESCRICAO END DESCRICAO_DIVISAO
        , op.DATA_ENTRADA_CORTE
        , ( SELECT
              MIN( l1.ORDEM_CONFECCAO )
            FROM PCPC_040 l1
            WHERE l1.ORDEM_PRODUCAO   = l.ORDEM_PRODUCAO
              AND l1.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
              AND l1.PROCONF_GRUPO    = l.PROCONF_GRUPO
              AND l1.PROCONF_SUBGRUPO = l.PROCONF_SUBGRUPO
              AND l1.PROCONF_ITEM     = l.PROCONF_ITEM
          ) OC1
        FROM (
          SELECT
            os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          , os.ORDEM_PRODUCAO
          , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
          , max( os.QTDE_PECAS_PROG ) QTDE_PECAS_PROG
          , max( os.QTDE_PECAS_PROD ) QTDE_PECAS_PROD
          , max( os.QTDE_CONSERTO ) QTDE_CONSERTO
          , max( os.QTDE_PECAS_2A ) QTDE_PECAS_2A
          , max( os.QTDE_PERDAS ) QTDE_PERDAS
          , max( CASE WHEN os.CODIGO_FAMILIA < 1000
                 THEN os.CODIGO_FAMILIA
                 ELSE 0 END ) DIVISAO
          , max( os.ROWID ) ROW_ID
          FROM PCPC_040 os
          WHERE 1=1
            {filtra_op} -- filtra_op
            {filtra_os} -- filtra_os
            {filtra_oc_ini} -- filtra_oc_ini
            {filtra_oc_fim} -- filtra_oc_fim
            {filtra_tam} -- filtra_tam
            {filtra_cor} -- filtra_cor
          GROUP BY
            os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          , os.ORDEM_PRODUCAO
        ) l
        LEFT JOIN PCPC_040 dos
          ON l.NUMERO_ORDEM <> 0
         AND dos.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
         AND dos.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
         AND dos.NUMERO_ORDEM = l.NUMERO_ORDEM
        LEFT JOIN MQOP_005 eos
          ON eos.CODIGO_ESTAGIO = dos.CODIGO_ESTAGIO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        JOIN BASI_030 ref
          ON ref.NIVEL_ESTRUTURA = '1'
         AND ref.REFERENCIA = l.PROCONF_GRUPO
        JOIN BASI_020 tam
          ON tam.BASI030_NIVEL030 = '1'
         AND tam.BASI030_REFERENC = l.PROCONF_GRUPO
         AND tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        JOIN BASI_010 r
          ON r.NIVEL_ESTRUTURA = '1'
         AND r.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND r.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
         AND r.ITEM_ESTRUTURA = l.PROCONF_ITEM
        LEFT JOIN BASI_180 di -- divisao de producao - unidade
          ON di.DIVISAO_PRODUCAO = l.DIVISAO
        LEFT JOIN OBRF_080 osc -- OS capa
          ON l.NUMERO_ORDEM <> 0
         AND osc.NUMERO_ORDEM = l.NUMERO_ORDEM
        LEFT JOIN BASI_180 dp -- divisao de producao - unidade
          ON dp.FACCIONISTA9 = osc.CGCTERC_FORNE9
         AND dp.FACCIONISTA4 = osc.CGCTERC_FORNE4
         AND dp.FACCIONISTA2 = osc.CGCTERC_FORNE2
        JOIN PCPC_020 op -- OP capa
          ON op.ordem_producao = l.ORDEM_PRODUCAO
        {sql_order} -- sql_order
        {sql_pos_qtd_lotes} -- sql_pos_qtd_lotes
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    for i in range(0, pula):
        if len(data) != 0:
            del(data[0])
    return data
