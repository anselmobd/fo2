from fo2.models import rows_to_dict_list

from lotes.models import *


def get_lotes(cursor, op='', os='', tam='', cor='', order='',
              oc_ini='', oc_fim='', pula=0, qtd_lotes=100000):
    # Lotes ordenados por OP + OS + referência + estágio
    if oc_ini == '':
        oc_ini = 0
    if oc_fim == '':
        oc_fim = 99999
    if pula is None:
        pula = 0
    if qtd_lotes is None:
        qtd_lotes = 100000
    sql = '''
        WITH Table_qtd_lotes AS (
        SELECT
          l.ORDEM_PRODUCAO OP
        , CASE WHEN dos.NUMERO_ORDEM IS NULL
          THEN '0'
          ELSE l.NUMERO_ORDEM || ' (' || eos.DESCRICAO || ')'
          END OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
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
              AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
          )
          , 'FINALIZADO'
          ) EST
        , l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        , l.QTDE_PECAS_PROG QTD
        , r.NARRATIVA
        , l.DIVISAO
        , di.DESCRICAO DESCRICAO_DIVISAO
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
          , max( os.CODIGO_FAMILIA ) DIVISAO
          FROM PCPC_040 os
          WHERE 1=1
            AND (os.ORDEM_PRODUCAO = %s or %s IS NULL)
            AND (os.NUMERO_ORDEM = %s or %s IS NULL)
            AND (os.ORDEM_CONFECCAO >= %s or %s IS NULL)
            AND (os.ORDEM_CONFECCAO <= %s or %s IS NULL)
            AND (os.PROCONF_SUBGRUPO = %s OR %s IS NULL)
            AND (os.PROCONF_ITEM = %s OR %s IS NULL)
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
        JOIN BASI_010 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND r.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
         AND r.ITEM_ESTRUTURA = l.PROCONF_ITEM
        LEFT JOIN BASI_180 di
          ON di.DIVISAO_PRODUCAO = l.DIVISAO
    '''
    if order == 'o':
        sql = sql + '''
            ORDER BY
              l.ORDEM_CONFECCAO
        '''
    elif order == 't':
        sql = sql + '''
            ORDER BY
              l.ORDEM_PRODUCAO
            , l.NUMERO_ORDEM
            , l.PROCONF_GRUPO
            , t.ORDEM_TAMANHO
            , l.PROCONF_ITEM
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO
        '''
    else:
        sql = sql + '''
            ORDER BY
              l.ORDEM_PRODUCAO
            , l.NUMERO_ORDEM
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO
        '''
    sql = sql + '''
        )
        select * from Table_qtd_lotes where rownum <= %s
    '''

    qtd_rows = pula + qtd_lotes
    cursor.execute(
        sql, [op, op, os, os, oc_ini, oc_ini, oc_fim, oc_fim,
              tam, tam, cor, cor, qtd_rows])
    data = rows_to_dict_list(cursor)
    for i in range(0, pula):
        del(data[0])
    return data


def get_os(cursor, os='', op='', periodo='', oc=''):
    # Informações sobre OS
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
        , sum(l.QTDE_PECAS_PROG) QTD
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
        JOIN pcpc_040 l
          ON l.NUMERO_ORDEM = os.NUMERO_ORDEM
        WHERE 1=1
          AND (os.NUMERO_ORDEM = %s or %s IS NULL)
          AND (l.ORDEM_PRODUCAO = %s or %s IS NULL)
          AND (l.PERIODO_PRODUCAO = %s or %s IS NULL)
          AND (l.ORDEM_CONFECCAO = %s or %s IS NULL)
          AND l.NUMERO_ORDEM <> 0
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
    """
    cursor.execute(sql, [os, os, op, op, periodo, periodo, oc, oc])
    return rows_to_dict_list(cursor)
