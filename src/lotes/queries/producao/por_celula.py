from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lm


__all__ = ['por_celula_query']


def por_celula_query(cursor, dada_de=None, dada_ate=None, celula=None, estagio=None):
    filtro_dada_de = lm(
        f"AND ml.DATA_PRODUCAO >= DATE '{dada_de}'"
    ) if dada_de else ''

    filtro_dada_ate = lm(
        f"AND ml.DATA_PRODUCAO <= DATE '{dada_ate}'"
    ) if dada_ate else ''

    filtro_celula = lm(
        f"AND l.CODIGO_FAMILIA = '{celula}'"
    ) if celula else ''

    filtro_estagio = lm(
        f"AND l.CODIGO_ESTAGIO = '{estagio}'"
    ) if estagio else ''

    sql = lm(f'''
        WITH mlseq AS
        ( SELECT 
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
        , CASE WHEN c.CGC_9 IS NULL THEN
            '-'
          ELSE  
            c.NOME_CLIENTE
            || ' (' || lpad(c.CGC_9, 8, '0')
            || '/' || lpad(c.CGC_4, 4, '0')
            || '-' || lpad(c.CGC_2, 2, '0')
            || ')'
          END CLIENTE
        , l.PROCONF_GRUPO ref
        , count(l.ORDEM_CONFECCAO) lotes
        , sum(l.QTDE_PECAS_PROD) qtd
        , sum(l.QTDE_PERDAS) perda
        FROM PCPC_040 l
        JOIN PCPC_020 op
          ON op.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
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
          {filtro_dada_de} -- filtro_dada_de
          {filtro_dada_ate} -- filtro_dada_ate
          {filtro_celula} -- filtro_celula
          {filtro_estagio} -- filtro_estagio
          AND l.QTDE_PECAS_PROD <> 0 
        GROUP BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
        , c.CGC_9
        , c.CGC_4
        , c.CGC_2
        , c.NOME_CLIENTE
        , l.PROCONF_GRUPO
        ORDER BY 
          ml.DATA_PRODUCAO
        , l.ORDEM_PRODUCAO
    ''')
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    for row in dados:
        row['data'] = row['data'].date()
    return dados
