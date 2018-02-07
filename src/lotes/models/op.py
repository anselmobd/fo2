from fo2.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *


def op_inform(cursor, op):
    # informações gerais
    sql = '''
        SELECT
          case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'B9999' then 'PG'
          else 'MD'
          end TIPO_REF
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0 THEN 'Filha de'
          WHEN ofi.ORDEM_PRODUCAO IS NOT NULL THEN 'Mãe de'
          ELSE 'Avulsa'
          END TIPO_OP
        , coalesce( ofi.ORDEM_PRODUCAO, o.ORDEM_PRINCIPAL ) OP_REL
        , o.SITUACAO ||
          CASE
          WHEN o.SITUACAO = 2 THEN '-Ordem conf. gerada'
          WHEN o.SITUACAO = 4 THEN '-Ordens em produção'
          WHEN o.SITUACAO = 9 THEN '-Ordem cancelada'
          ELSE ' '
          END SITUACAO
        , o.COD_CANCELAMENTO ||
          CASE
          WHEN o.COD_CANCELAMENTO = 0 THEN ''
          ELSE '-' || COALESCE(c.DESCRICAO, '')
          END CANCELAMENTO
        , o.ALTERNATIVA_PECA ALTERNATIVA
        , o.ROTEIRO_PECA ROTEIRO
        , o.REFERENCIA_PECA REF
        , COALESCE(
          CASE WHEN o.REFERENCIA_PECA < 'C0000' THEN
            CAST( CAST( regexp_replace(o.REFERENCIA_PECA, '[^0-9]', '')
                        AS INTEGER ) AS VARCHAR2(5) )
          ELSE
            ( SELECT
                CAST( MAX(
                  CASE WHEN ec.GRUPO_ITEM IS NULL THEN 0
                  ELSE CAST( regexp_replace(ec.GRUPO_ITEM, '[^0-9]', '')
                             AS INTEGER )
                  END
                ) AS VARCHAR2(5) )
                FROM BASI_050 ec
                JOIN BASI_030 rr
                  ON rr.NIVEL_ESTRUTURA = ec.NIVEL_ITEM
                 AND rr.REFERENCIA = ec.GRUPO_ITEM
                 AND rr.RESPONSAVEL IS NOT NULL
                WHERE ec.NIVEL_COMP = 1
                  AND ec.GRUPO_COMP = o.REFERENCIA_PECA
            )
          END
          , ' ' ) MODELO
        , ( SELECT
              COUNT( DISTINCT l.ORDEM_CONFECCAO )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) LOTES
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          ) QTD
        , o.DATA_PROGRAMACAO DT_DIGITACAO
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO PERIODO_INI
        , p.DATA_FIM_PERIODO PERIODO_FIM
        , o.DEPOSITO_ENTRADA || ' - ' || d.DESCRICAO DEPOSITO
        , o.PEDIDO_VENDA PEDIDO
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PED_CLIENTE
        , r.NUMERO_MOLDE MOLDE
        FROM PCPC_020 o
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
        LEFT JOIN pcpt_050 c
          ON c.COD_CANCELAMENTO = o.COD_CANCELAMENTO
        LEFT JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.ORDEM_PRODUCAO
        JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = o.DEPOSITO_ENTRADA
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        WHERE o.ORDEM_PRODUCAO = %s
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          ll.EST
        , ll.COD_EST
        , (SELECT
              cast( SUM( lp.QTDE_PECAS_PROD ) / SUM( lp.QTDE_PECAS_PROG ) * 100
                    AS NUMERIC(10,2) )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) PERC
        , (SELECT
              SUM( lp.QTDE_PECAS_PROD )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) PROD
        , (SELECT
              SUM( lp.QTDE_PECAS_2A )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) Q2
        , (SELECT
              SUM( lp.QTDE_PERDAS )
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
          ) PERDA
        , (SELECT
              count(*)
            FROM pcpc_040 lp
            WHERE lp.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
              AND lp.SEQ_OPERACAO = ll.SEQ_OPERACAO
              AND lp.QTDE_EM_PRODUCAO_PACOTE <> 0
          ) LOTES
        FROM
        (
        SELECT DISTINCT
          l.ORDEM_PRODUCAO
        , l.SEQ_OPERACAO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.CODIGO_ESTAGIO COD_EST
        FROM pcpc_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.ORDEM_PRODUCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        ) ll
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_sortimento(cursor, op):
    # Grade de OP
    grade = GradeQtd(cursor, [op])

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql='''
            SELECT DISTINCT
              i.TAMANHO
            , i.SEQUENCIA_TAMANHO
            FROM PCPC_021 i
            WHERE i.ORDEM_PRODUCAO = %s
            ORDER BY
              i.SEQUENCIA_TAMANHO
        '''
        )

    # cores
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Cor',
        name_plural='Cores',
        sql='''
            SELECT
              i.SORTIMENTO
            , i.SORTIMENTO || ' - ' || max( p.DESCRICAO_15 ) DESCR
            FROM PCPC_021 i
            JOIN pcpc_020 op
              ON op.ORDEM_PRODUCAO = i.ORDEM_PRODUCAO
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = op.REFERENCIA_PECA
             AND p.ITEM_ESTRUTURA = i.SORTIMENTO
            WHERE i.ORDEM_PRODUCAO = %s
            GROUP BY
              i.SORTIMENTO
            ORDER BY
              2
        '''
        )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
            SELECT
              i.TAMANHO
            , i.SORTIMENTO
            , i.QUANTIDADE
            FROM PCPC_021 i
            WHERE i.ORDEM_PRODUCAO = %s
            ORDER BY
              i.SEQUENCIA_TAMANHO
            , i.SORTIMENTO
        '''
        )

    return (grade.table_data['header'], grade.table_data['fields'],
            grade.table_data['data'])


def op_lotes(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, op=op, order='e')


def op_ref_estagio(cursor, op):
    # Totais por referência + estágio
    sql = '''
        SELECT
          lote.REF
        , lote.TAM
        , lote.COR
        , lote.EST
        , count(*) LOTES
        , sum(lote.QTD) QTD
        FROM (
          SELECT
            l.PROCONF_GRUPO REF
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
          , l.QTDE_PECAS_PROG QTD
          FROM (
            SELECT
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
            , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
            , max( os.QTDE_PECAS_PROG ) QTDE_PECAS_PROG
            FROM PCPC_040 os
            WHERE os.ORDEM_PRODUCAO = %s
            GROUP BY
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
          ) l
        ) lote
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = lote.TAM
        GROUP BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.TAM
        , lote.EST
        ORDER BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.EST
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_get_os(cursor, op):
    # Informações sobre OS
    return get_os(cursor, op=op)


def op_os_ref(cursor, op):
    # Totais por OS + referência
    sql = """
        SELECT
          l.NUMERO_ORDEM OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , count( l.ORDEM_CONFECCAO ) LOTES
        , SUM (
            ( SELECT
                q.QTDE_PECAS_PROG
              FROM PCPC_040 q
              WHERE q.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                AND q.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND q.SEQ_OPERACAO = (
                  SELECT
                    min(o.SEQ_OPERACAO)
                  FROM PCPC_040 o
                  WHERE o.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                    AND o.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                )
            )
          ) QTD
        FROM (
          SELECT DISTINCT
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          FROM PCPC_040 os
          WHERE os.ORDEM_PRODUCAO = %s
          GROUP BY
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
        ) l
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        GROUP BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
        ORDER BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)
