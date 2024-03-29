import collections.abc
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['cd_bonus_query']


def cd_bonus_query(
    cursor,
    data=None,
    usuario=None,
    detalhe=None,
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

    detalhe_oc = f", d.OC " if detalhe == 'oc' else ''

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
            ml.USUARIO
          , ml.REF
          , ml.OP
          , ml.OC
          , ml.DT
          , ml.QTD
          , resh.GRUPO_DESTINO REF_DEST
          , CASE WHEN
              REGEXP_LIKE(
                resh.GRUPO_DESTINO,
               '^[0-9]*[0-9A]$'
              )
            THEN 'varejo'
            ELSE 'atacado'
            END DEST
          , sum(resh.QTDE) QTD_RES
          FROM move_lote ml
          JOIN PCPC_044 res
            ON res.ORDEM_PRODUCAO = ml.OP
           AND res.ORDEM_CONFECCAO = ml.OC
          JOIN PCPC_044_HIST resh
            ON resh.ORDEM_PRODUCAO = res.ORDEM_PRODUCAO
           AND resh.ORDEM_CONFECCAO = res.ORDEM_CONFECCAO
           AND resh.SOLICITACAO = res.SOLICITACAO
           AND resh.PEDIDO_DESTINO = res.PEDIDO_DESTINO
           AND resh.OP_DESTINO = res.OP_DESTINO
           AND resh.ALTER_DESTINO = res.ALTER_DESTINO
           AND resh.GRUPO_DESTINO = res.GRUPO_DESTINO
           AND resh.SUB_DESTINO = res.SUB_DESTINO
           AND resh.COR_DESTINO = res.COR_DESTINO
           AND resh.CAMBIO >= ml.DT
           AND resh.CAMBIO <= ml.DT + 1/24/60/60 * 3
           AND resh.SITUACAO = 5
          GROUP BY 
            ml.USUARIO
          , ml.REF
          , ml.OP
          , ml.OC
          , ml.DT
          , ml.QTD
          , resh.GRUPO_DESTINO
          , CASE WHEN
              REGEXP_LIKE(
                resh.GRUPO_DESTINO,
               '^[0-9]*[0-9A]$'
              )
            THEN 'varejo'
            ELSE 'atacado'
            END
        )
        SELECT 
          d.USUARIO
        , d."REF"
        , d.OP
        {detalhe_oc} -- detelhe_oc
        , d.REF_DEST
        , d.DEST
        , sum(d.QTD) QTD
        , sum(d.QTD_RES) QTD_RES
        FROM destino d
        GROUP BY 
          d.USUARIO
        , d."REF"
        , d.OP
        {detalhe_oc} -- detelhe_oc
        , d.REF_DEST
        , d.DEST
        ORDER BY 
          d.DEST
        , d.USUARIO
        , d."REF"
        , d.OP
        {detalhe_oc} -- detelhe_oc
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)

    return data
