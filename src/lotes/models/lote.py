from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


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


def posicao2_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        WITH lotes AS (
        SELECT
          %s PERIODO_PRODUCAO
        , %s ORDEM_CONFECCAO
        FROM SYS.DUAL
        )
        (
        SELECT
          0 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PECAS_PROD QTD
        , 'FINALIZADO 1A.' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO || ' (ULTIMO)' ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PECAS_PROD <> 0
          AND l.SEQUENCIA_ESTAGIO
              = (
                SELECT
                  max(ms.SEQUENCIA_ESTAGIO)
                FROM PCPC_040 ms
                WHERE ms.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
                  AND ms.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
              )
        --
        UNION
        --
        SELECT
          1000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PECAS_2A QTD
        , 'FINALIZADO 2A.' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO || ' (ULTIMO)' ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PECAS_2A <> 0
          AND l.SEQUENCIA_ESTAGIO
              = (
                SELECT
                  max(ms.SEQUENCIA_ESTAGIO)
                FROM PCPC_040 ms
                WHERE ms.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
                  AND ms.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
              )
        --
        UNION
        --
        SELECT
          2000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO QTD
        , 'A PRODUZIR' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO <> 0
        --
        UNION
        --
        SELECT
          3000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_CONSERTO QTD
        , 'EM CONSERTO' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_CONSERTO <> 0
        --
        UNION
        --
        SELECT
          4000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PERDAS QTD
        , 'PERDAS' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PERDAS <> 0
        )
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


def posicao_get_os(cursor, periodo, oc):
    # Informações sobre OS
    return get_os(cursor, periodo=periodo, oc=oc)


def posicao_get_op(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        , l.SITUACAO_ORDEM SITU
        , TO_CHAR(o.DATA_HORA, 'DD/MM/YYYY HH24:MI') DT
        , TO_CHAR(o.DATA_ENTRADA_CORTE, 'DD/MM/YYYY') DT_CORTE
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
        , l.QTDE_PECAS_PROG QTDE
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , case
          when l.PROCONF_GRUPO <= '99999' then 'PA'
          when l.PROCONF_GRUPO <= 'A9999' then 'PG'
          else 'MD'
          end TIPO
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


def posicao_so_estagios(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO COD_EST
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
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
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)


def posicao_historico(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY HH24:MI:SS') DT
        , h.PCPC040_ESTCONF EST
        , h.TURNO_PRODUCAO TURNO
        , h.CODIGO_FAMILIA FAMILIA
        , h.QTDE_PRODUZIDA Q_P1
        , h.QTDE_PECAS_2A Q_P2
        , h.QTDE_CONSERTO Q_C
        , h.QTDE_PERDAS Q_P
        , coalesce(h.USUARIO_SYSTEXTIL, ' ') USU
        , coalesce(h.PROCESSO_SYSTEXTIL, ' ') PRG
        , coalesce(p.DESCRICAO, ' ') PRG_DESCR
        FROM PCPC_045 h
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = h.PROCESSO_SYSTEXTIL
         AND p.LOCALE = 'pt_BR'
        WHERE h.PCPC040_PERCONF = %s
          AND h.PCPC040_ORDCONF = %s
        ORDER BY
          h.DATA_INSERCAO
        , h.PCPC040_ESTCONF
        , h.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)
