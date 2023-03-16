from pprint import pprint

from utils.functions.models.dictlist import dictlist

from utils.functions.queries import debug_cursor_execute


__all = ['query']


def query(
    cursor,
    op=None,
):
    filtra_op = ""
    if op is not None and op != '':
        filtra_op = f"""--
            AND o.ORDEM_PRODUCAO = '{op}'
        """

    sql = f'''
        SELECT
          o.ORDEM_PRODUCAO OP
        , case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'A9999' then 'PG'
          when o.REFERENCIA_PECA <= 'B9999' then 'PB'
          when o.REFERENCIA_PECA LIKE 'F%' then 'MP'
          else 'MD'
          end TIPO_REF
        , o.SITUACAO COD_SITUACAO
        , o.SITUACAO ||
          CASE
          WHEN o.SITUACAO = 2 THEN '-Ordem conf. gerada'
          WHEN o.SITUACAO = 4 THEN '-Ordens em produção'
          WHEN o.SITUACAO = 9 THEN '-Ordem cancelada'
          ELSE ' '
          END SITUACAO
        , o.REFERENCIA_PECA REF
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , r.DESCR_REFERENCIA DESCR_REF
        , r.COLECAO
        FROM pcpc_020 o
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        WHERE 1=1
          {filtra_op} -- filtra_op
    '''
    debug_cursor_execute(cursor, sql)
    dados = dictlist(cursor)
    return dados
