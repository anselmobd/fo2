from utils.functions.models import rows_to_dict_list, GradeQtd

import lotes.queries as queries


def os_op(cursor, os):
    # Totais por OP
    sql = """
        SELECT
          l.ORDEM_PRODUCAO OP
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
        , o.PEDIDO_VENDA PEDIDO
        , COALESCE(ped.COD_PED_CLIENTE, '') PED_CLIENTE
        FROM pcpc_040 l -- lotes
        JOIN PCPC_020 o -- OP
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
        WHERE l.NUMERO_ORDEM = %s
        GROUP BY
          l.ORDEM_PRODUCAO
        , o.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)


def os_sortimento(cursor, os):
    # Grade de OS
    grade = GradeQtd(cursor, [os])

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql='''
            SELECT DISTINCT
              s.PRODORD_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO
            FROM OBRF_081 s
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = s.PRODORD_SUBGRUPO
            WHERE s.NUMERO_ORDEM = %s
            ORDER BY
              tam.ORDEM_TAMANHO
        '''
        )

    # cores
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Produto-Cor',
        name_plural='Produtos-Cores',
        sql='''
            SELECT
              s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM SORTIMENTO
            , s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM || ' - ' ||
              max( p.DESCRICAO_15 ) DESCR
            FROM OBRF_081 s
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = s.PRODORD_GRUPO
             AND p.ITEM_ESTRUTURA = s.PRODORD_ITEM
            WHERE s.NUMERO_ORDEM = %s
            GROUP BY
              s.PRODORD_GRUPO
            , s.PRODORD_ITEM
            ORDER BY
              2
        '''
        )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
            SELECT
              s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM SORTIMENTO
            , s.PRODORD_SUBGRUPO TAMANHO
            , s.QTDE_ARECEBER QUANTIDADE
            FROM OBRF_081 s
            WHERE s.NUMERO_ORDEM = %s
        '''
        )

    return (grade.table_data['header'], grade.table_data['fields'],
            grade.table_data['data'])
