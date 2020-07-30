from utils.functions.models import rows_to_dict_list


def posicao_historico(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY HH24:MI:SS') DT
        , h.DATA_PRODUCAO DT_PROD
        , h.PCPC040_ESTCONF EST
        , h.TURNO_PRODUCAO TURNO
        , h.CODIGO_FAMILIA FAMILIA
        , h.QTDE_PRODUZIDA Q_P1
        , h.QTDE_PECAS_2A Q_P2
        , h.QTDE_CONSERTO Q_C
        , h.QTDE_PERDAS Q_P
        , coalesce(u.USUARIO, ' ') USU
        , coalesce(p.CODIGO_PROGRAMA, ' ') PRG
        , coalesce(p.DESCRICAO, ' ') PRG_DESCR
        FROM PCPC_045 h
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = h.PROCESSO_SYSTEXTIL
         AND p.LOCALE = 'pt_BR'
         AND SUBSTR(h.USUARIO_SYSTEXTIL,0,1) != '*'
        LEFT JOIN HDOC_030 u
          ON u.EMRPESA = 1
         AND u.CODIGO_USUARIO = h.CODIGO_USUARIO
        WHERE h.PCPC040_PERCONF = %s
          AND h.PCPC040_ORDCONF = %s
        ORDER BY
          h.DATA_INSERCAO
        , h.PCPC040_ESTCONF
        , h.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)
