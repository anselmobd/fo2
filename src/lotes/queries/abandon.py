from pprint import pprint

from utils.functions.models.dictlist import dictlist


def posicao_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          el.CODIGO_ESTAGIO
        , el.DESCRICAO DESCRICAO_ESTAGIO
        FROM (
        SELECT
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND l.QTDE_EM_PRODUCAO_PACOTE <> 0
        UNION
        SELECT
          0
        , 'FINALIZADO'
        from dual
        ORDER BY
          1 DESC
        ) el
        WHERE rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return dictlist(cursor)


def posicao_estagios(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.QTDE_PROGRAMADA Q_PROG
        , l.QTDE_PECAS_PROG Q_P
        , l.QTDE_A_PRODUZIR_PACOTE Q_AP
        , l.QTDE_EM_PRODUCAO_PACOTE Q_EP
        , l.QTDE_PECAS_PROD Q_PROD
        , l.QTDE_PECAS_2A Q_2A
        , l.QTDE_PERDAS Q_PERDA
        , l.QTDE_CONSERTO Q_CONSERTO
        , l.CODIGO_FAMILIA FAMI
        , l.NUMERO_ORDEM OS
        , coalesce(u.USUARIO, ' ') USU
        , TO_CHAR(d.DATA_INSERCAO, 'DD/MM/YYYY HH24:MI') DT
        , coalesce(d.PROCESSO_SYSTEXTIL || ' - ' || p.DESCRICAO, ' ') PRG
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        LEFT JOIN PCPC_045 d
          ON d.PCPC040_PERCONF = l.PERIODO_PRODUCAO
         AND d.PCPC040_ORDCONF = l.ORDEM_CONFECCAO
         AND d.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = d.PROCESSO_SYSTEXTIL
         AND p.LOCALE = 'pt_BR'
        LEFT JOIN HDOC_030 u
          ON u.EMPRESA = 1
         AND u.CODIGO_USUARIO = d.CODIGO_USUARIO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        , d.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = dictlist(cursor)
    for row in data:
        if row['DT'] is None:
            row['DT'] = ''
    return data
