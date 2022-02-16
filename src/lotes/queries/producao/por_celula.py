from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, dada_de=None, dada_ate=None, celula=-1, estagio=-1):
    filtro_dada_de = (
        f"AND ml.DATA_PRODUCAO >= '{dada_de}'"
    ) if dada_de else ''

    filtro_dada_ate = (
        f"AND ml.DATA_PRODUCAO <= '{dada_ate}'"
    ) if dada_ate else ''

    filtro_celula = (
        f"AND l.CODIGO_FAMILIA = '{celula}'"
    ) if celula != -1 else ''

    filtro_estagio = (
        f"AND l.CODIGO_ESTAGIO = '{estagio}'"
    ) if estagio != -1 else ''

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
        , l.PROCONF_GRUPO ref
        , count(l.ORDEM_CONFECCAO) lotes
        , sum(l.QTDE_PECAS_PROD) qtd
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
        WHERE 1=1
          -- AND ml.DATA_PRODUCAO = DATE '2022-02-15'
          {filtro_dada_de} -- filtro_dada_de
          {filtro_dada_ate} -- filtro_dada_ate
          -- AND l.CODIGO_FAMILIA = 2836
          {filtro_celula} -- filtro_celula
          -- AND l.CODIGO_ESTAGIO = 33
          {filtro_estagio} -- filtro_estagio
          AND l.QTDE_PECAS_PROD <> 0 
        GROUP BY 
          ml.DATA_PRODUCAO
        , l.PROCONF_GRUPO
        ORDER BY 
          ml.DATA_PRODUCAO
    '''
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)
    for row in dados:
        row['data'] = row['data'].date()
    return dados
