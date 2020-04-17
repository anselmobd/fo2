from utils.functions.models import rows_to_dict_list, GradeQtd


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
