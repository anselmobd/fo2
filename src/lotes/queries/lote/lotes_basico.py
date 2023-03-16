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
            , ot.ORDEM_TAMANHO
            , l.PERIODO_PRODUCAO
            , l.ORDEM_CONFECCAO
        '''

    sql = f'''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        , r.COLECAO
        , r.DESCR_REFERENCIA
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , ot.ORDEM_TAMANHO
        , t.DESCR_TAM_REFER DESCR_TAMANHO
        , l.PROCONF_ITEM COR
        , i.DESCRICAO_15 DESCR_COR
        , i.NARRATIVA
        , l.QTDE_PECAS_PROG QTD
        FROM PCPC_040 l
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = '1'
         AND r.REFERENCIA = l.PROCONF_GRUPO
        JOIN BASI_020 t
          ON t.BASI030_NIVEL030 = '1'
         AND t.BASI030_REFERENC = l.PROCONF_GRUPO
         AND t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = '1'
         AND i.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND i.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
         AND i.ITEM_ESTRUTURA = l.PROCONF_ITEM
        LEFT JOIN BASI_220 ot
          ON ot.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          {filtra_op} -- filtra_op
          AND l.SEQUENCIA_ESTAGIO = 1
        {sql_order} -- sql_order
    '''

    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
