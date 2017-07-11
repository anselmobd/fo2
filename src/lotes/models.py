from django.db import models

from fo2.models import rows_to_dict_list


def existe_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT DISTINCT
          l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


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
    return rows_to_dict_list(cursor)


def posicao_periodo_oc(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , TO_CHAR(p.DATA_INI_PERIODO, 'DD/MM/YYYY') INI
        , TO_CHAR(p.DATA_FIM_PERIODO - 1, 'DD/MM/YYYY') FIM
        , %s OC
        FROM PCPC_010 p
        WHERE p.AREA_PERIODO = 1
          AND p.PERIODO_PRODUCAO = %s
    '''
    cursor.execute(sql, [ordem_confeccao, periodo])
    return rows_to_dict_list(cursor)


def posicao_get_op(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        , l.SITUACAO_ORDEM SITU
        , TO_CHAR(o.DATA_HORA, 'DD/MM/YYYY HH24:MI') DT
        FROM PCPC_040 l
        JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = l.NOME_PROGRAMA_CRIACAO
         AND p.LOCALE = 'pt_BR'
        LEFT JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) != 0:
        situacoes = {
            1: 'ORDEM CONF. GERADA',
            2: 'ORDENS EM PRODUCAO',
            9: 'ORDEM CANCELADA',
        }
        for row in data:
            if row['SITU'] in situacoes:
                row['SITU'] = '{} - {}'.format(
                    row['SITU'], situacoes[row['SITU']])
    return data


def posicao_get_item(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.PROCONF_NIVEL99
          || '.' || l.PROCONF_GRUPO
          || '.' || l.PROCONF_SUBGRUPO
          || '.' || l.PROCONF_ITEM ITEM
        , i.NARRATIVA NARR
        , l.QTDE_PROGRAMADA QTDE
        FROM PCPC_040 l
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND i.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND i.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
         AND i.ITEM_ESTRUTURA = l.PROCONF_ITEM
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


def posicao_estagios(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.QTDE_PROGRAMADA Q_P
        , l.QTDE_EM_PRODUCAO_PACOTE Q_EP
        , l.QTDE_A_PRODUZIR_PACOTE Q_AP
        , l.CODIGO_FAMILIA FAMI
        , l.NUMERO_ORDEM OS
        , coalesce(d.USUARIO_SYSTEXTIL, ' ') USU
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
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        , d.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    for row in data:
        if row['DT'] is None:
            row['DT'] = ''
    return data
