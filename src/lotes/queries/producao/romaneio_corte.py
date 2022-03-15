from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, data=None):
    filtro_data = (
        f"AND ml.DATA_PRODUCAO = '{data}'"
    ) if data else ''

    sql = f'''
        WITH mlseq AS
        (
        SELECT 
          ml.PCPC040_PERCONF per
        , ml.PCPC040_ORDCONF ord
        , ml.PCPC040_ESTCONF est
        , max(ml.SEQUENCIA) seq
        FROM  PCPC_045 ml
        GROUP BY
          ml.PCPC040_PERCONF
        , ml.PCPC040_ORDCONF
        , ml.PCPC040_ESTCONF
        ) 
        SELECT
          TO_DATE(ml.DATA_PRODUCAO) data
        , l.ORDEM_PRODUCAO op
        , l.PROCONF_GRUPO ref
        , l.PROCONF_SUBGRUPO tam
        , l.PROCONF_ITEM cor
        , count(l.ORDEM_CONFECCAO) lotes
        , sum(l.QTDE_PECAS_PROD) qtd
        , sum(l.QTDE_PERDAS) perda
        FROM PCPC_040 l
        JOIN mlseq mls
          ON mls.per = l.PERIODO_PRODUCAO
         AND mls.ord = l.ORDEM_CONFECCAO
         AND mls.est = l.CODIGO_ESTAGIO
        JOIN PCPC_045 ml
          ON ml.PCPC040_PERCONF = l.PERIODO_PRODUCAO
         AND ml.PCPC040_ORDCONF = l.ORDEM_CONFECCAO 
         AND ml.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
         AND ml.SEQUENCIA = mls.seq
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          -- AND ml.DATA_PRODUCAO = DATE '2022-02-15'
          {filtro_data} -- filtro_data
          AND l.CODIGO_ESTAGIO = 16
          AND l.QTDE_PECAS_PROD <> 0 
        GROUP BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        ORDER BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
    '''
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)
    for row in dados:
        row['data'] = row['data'].date()
    return dados
