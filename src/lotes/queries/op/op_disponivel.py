from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, op):
    sql = f"""
        WITH
          lotes AS
        ( SELECT 
            l.ORDEM_PRODUCAO OP
          , l.PERIODO_PRODUCAO PER
          , l.ORDEM_CONFECCAO OC
          , l.PROCONF_NIVEL99 NIVEL
          , l.PROCONF_GRUPO REF
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          , min(QTDE_PROGRAMADA) QPROG
          , sum(l.QTDE_EM_PRODUCAO_PACOTE) QEMPROD
          FROM PCPC_040 l -- lotes
          WHERE l.ORDEM_PRODUCAO = {op}
          GROUP BY 
            l.ORDEM_PRODUCAO
          , l.PERIODO_PRODUCAO 
          , l.ORDEM_CONFECCAO 
          , l.PROCONF_NIVEL99
          , l.PROCONF_GRUPO
          , l.PROCONF_SUBGRUPO
          , l.PROCONF_ITEM
        ),
          solicitados AS
        ( SELECT 
            l.OP
          , l.PER 
          , l.OC 
          , l.NIVEL
          , l.REF
          , l.TAM
          , l.COR
          , l.QPROG
          , l.QEMPROD
          , COALESCE(SUM(sl.QTDE), 0) QEMP
          --, l.QPROG - sum(sl.QTDE) QPROGDISP
          --, l.QEMPROD - sum(sl.QTDE) QEMPRODDISP
          FROM lotes l
          LEFT JOIN PCPC_044 sl -- solicitação lote
            ON sl.ORDEM_PRODUCAO = l.op
           AND sl.ORDEM_CONFECCAO = l.OC 
           AND sl.SITUACAO IN (1, 2, 3, 4)
          GROUP BY 
            l.OP
          , l.PER 
          , l.OC 
          , l.NIVEL
          , l.REF
          , l.TAM
          , l.COR
          , l.QPROG
          , l.QEMPROD
        )
        SELECT 
          s.NIVEL
        , s.REF
        , COALESCE(tam.ORDEM_TAMANHO, 0) ordem_tam
        , s.TAM
        , s.COR
        --, sum(s.QEMPRODDISP) QTD
        , sum(s.QEMPROD - s.QEMP) QTD
        FROM solicitados s
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = s.TAM
        GROUP BY 
          s.NIVEL
        , s.REF
        , tam.ORDEM_TAMANHO
        , s.TAM
        , s.COR
        ORDER BY 
          s.NIVEL
        , s.REF
        , tam.ORDEM_TAMANHO
        , s.TAM
        , s.COR
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
