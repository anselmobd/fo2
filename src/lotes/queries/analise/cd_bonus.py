import collections.abc
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['cd_bonus_query']


def cd_bonus_query(
    cursor,
    data=None,
    usuario=None,
):
    filtra_data = f"""--
        AND ml.DATA_PRODUCAO >= DATE '{data}'
        AND ml.DATA_PRODUCAO < DATE '{data}' + 1
    """ if data else ''

    if (not isinstance(usuario, collections.abc.Sequence)) or isinstance(usuario, str):
        usuario = (usuario, )
    filtra_usuario = f"""--
        AND ml.CODIGO_USUARIO IN ({', '.join(map(str, usuario))})
    """

    sql = f"""
        WITH
          move_lote AS
        ( SELECT
            u.USUARIO
          , l.PROCONF_GRUPO REF
          , l.ORDEM_PRODUCAO OP
          , l.ORDEM_CONFECCAO OC
          , ml.DATA_PRODUCAO DT
          , sum(ml.QTDE_PRODUZIDA) qtd
          --, ml.*
          FROM PCPC_045 ml
          JOIN PCPC_040 l
            ON l.PERIODO_PRODUCAO = ml.PCPC040_PERCONF 
           AND l.ORDEM_CONFECCAO = ml.PCPC040_ORDCONF 
           AND l.CODIGO_ESTAGIO = ml.PCPC040_ESTCONF 
          JOIN PCPC_020 op
            ON op.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO 
          JOIN HDOC_030 u 
            ON u.CODIGO_USUARIO = ml.CODIGO_USUARIO
          WHERE 1=1
            {filtra_data} -- filtra_data
            {filtra_usuario} -- filtra_usuario
            AND ml.PCPC040_ESTCONF = 63
          GROUP BY 
            u.USUARIO
          , l.PROCONF_GRUPO
          , l.ORDEM_PRODUCAO
          , l.ORDEM_CONFECCAO
          , ml.DATA_PRODUCAO
        )
        , destino AS
        ( SELECT 
            ml.*
          , resh.GRUPO_DESTINO REF_DEST
          , CASE WHEN
              REGEXP_LIKE(
                resh.GRUPO_DESTINO,
               '^[0-9]*[0-9A]$'
              )
            THEN 'varejo'
            ELSE 'atacado'
            END DEST
          FROM move_lote ml
          JOIN PCPC_044 res
            ON res.ORDEM_PRODUCAO = ml.OP
           AND res.ORDEM_CONFECCAO = ml.OC
          JOIN PCPC_044_HIST resh
            ON resh.ORDEM_PRODUCAO = res.ORDEM_PRODUCAO
           AND resh.ORDEM_CONFECCAO = res.ORDEM_CONFECCAO
           AND resh.SOLICITACAO = res.SOLICITACAO
           AND resh.CAMBIO = ml.DT
           AND resh.SITUACAO = 5
        )
        SELECT 
          d.USUARIO
        , d."REF"
        , d.OP
        , d.REF_DEST
        , d.DEST
        , sum(d.QTD) QTD
        FROM destino d
        GROUP BY 
          d.USUARIO
        , d."REF"
        , d.OP
        , d.REF_DEST
        , d.DEST
        ORDER BY 
          d.DEST
        , d.USUARIO
        , d."REF"
        , d.OP
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)

    return data
