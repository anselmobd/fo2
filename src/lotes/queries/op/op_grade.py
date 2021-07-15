from utils.functions.models import GradeQtd

from utils.functions import arg_def


def sql_op_sort_tam(op):
    sql = f'''
        SELECT DISTINCT
          l.PROCONF_SUBGRUPO TAMANHO
        , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
        FROM PCPC_040 l
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE l.ORDEM_PRODUCAO = {op}
        ORDER BY
          tam.ORDEM_TAMANHO
    '''
    return sql


def sql_op_sort_cor(op, descr_sort):
    if descr_sort:
        sql = f'''
            SELECT DISTINCT
              l.PROCONF_ITEM SORTIMENTO
            , l.PROCONF_ITEM || ' - ' || p.DESCRICAO_15 DESCR
            FROM PCPC_040 l
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = '1'
            AND p.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
            AND p.ITEM_ESTRUTURA = l.PROCONF_ITEM
            WHERE l.ORDEM_PRODUCAO = {op}
            ORDER BY
              l.PROCONF_ITEM
        '''
    else:
        sql = f'''
            SELECT DISTINCT
              l.PROCONF_ITEM SORTIMENTO
            , l.PROCONF_ITEM DESCR
            FROM PCPC_040 l
            WHERE l.ORDEM_PRODUCAO = {op}
            ORDER BY
              l.PROCONF_ITEM
        '''
    return sql


def sql_op_sort_grade(op, tipo):
    if tipo == 't':
        get_seq = 'min(l.SEQUENCIA_ESTAGIO)'
        get_qtd = 'sum(l.QTDE_PECAS_PROG)'
    elif tipo == 's':
        get_seq = 'max(l.SEQUENCIA_ESTAGIO)'
        get_qtd = 'sum(l.QTDE_PECAS_2A)'

    sql = f'''
        WITH
        filtro AS (
        SELECT 
          {op} OP
        FROM dual
        ),
        seq AS (
          SELECT
            {get_seq} SEQ
          FROM filtro
          JOIN PCPC_040 l
            ON l.ORDEM_PRODUCAO = filtro.OP
        ),
        filt_seq AS (
          SELECT 
            f.OP
          , s.SEQ
          FROM filtro f, seq s
        )
        SELECT 
          l.PROCONF_SUBGRUPO TAMANHO
        , l.PROCONF_ITEM SORTIMENTO
        , {get_qtd} QUANTIDADE
        FROM filt_seq fs
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = fs.OP
         AND l.SEQUENCIA_ESTAGIO = fs.SEQ
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        GROUP BY
          tam.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        ORDER BY
          tam.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    '''
    return sql


def op_grade(cursor, op, tipo='t', descr_sort=True):
    '''Retorna
      header, fields, data
    com grade de OP.

    Recebe: cursor, OP
    tipo:>t - Todos os lotes
          s - Segunda qualidade
    descr_sort: False - Apenas código do sortimento (cor)
               >True - Descrição junto ao código do sortimento (cor)
    '''
    grade = GradeQtd(cursor)

    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql=sql_op_sort_tam(op)
    )

    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Cor',
        name_plural='Cores',
        sql=sql_op_sort_cor(op, descr_sort)
    )

    grade.value(
        id='QUANTIDADE',
        sql=sql_op_sort_grade(op, tipo)
    )

    result = (
        grade.table_data['header'],
        grade.table_data['fields'],
        grade.table_data['data'],
        grade.total,
    )
    return result
