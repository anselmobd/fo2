from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


__all__ = ['query']


def query(
    cursor,
    op=None,
    order=None,
):

    filtra_op = f'''--
        AND l.ORDEM_PRODUCAO = '{op}'
    ''' if op else ''

    if order == 'r':  # referência + cor + tamanho + OC
        sql_order = '''--
            ORDER BY
              l.ORDEM_PRODUCAO
            , l.PROCONF_GRUPO
            , l.PROCONF_ITEM
            , t.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO
        '''

    sql = f'''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        , r.COLECAO
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM COR
        , l.QTDE_PECAS_PROG QTD
        FROM PCPC_040 l
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = '1'
         AND r.REFERENCIA = l.PROCONF_GRUPO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          {filtra_op} -- filtra_op
          AND l.SEQUENCIA_ESTAGIO = 1
        {sql_order} -- sql_order
    '''

    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
