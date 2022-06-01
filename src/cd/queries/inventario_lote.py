from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import periodo_oc


def get_qtd_lotes_63(cursor, lotes):
    if not lotes:
        return []

    if isinstance(lotes, (int, str)):
        lotes = [lotes]

    filtros_periodo_oc = []
    for lote in lotes:
        periodo, oc = periodo_oc(lote)
        filtros_periodo_oc.append(
            f"""--
                l.PERIODO_PRODUCAO = {periodo}
                AND l.ORDEM_CONFECCAO = {oc}
            """
        )
    filtro_periodos_ocs = " OR ".join(filtros_periodo_oc)

    sql = f"""
        SELECT
          l.PERIODO_PRODUCAO*100000+l.ORDEM_CONFECCAO lote
        , l.PERIODO_PRODUCAO periodo
        , l.ORDEM_CONFECCAO oc
        , l.ORDEM_PRODUCAO op
        , l.QTDE_DISPONIVEL_BAIXA qtd
        , l.QTDE_PECAS_PROG qtd_ori
        , l.QTDE_PECAS_PROD + l.QTDE_A_PRODUZIR_PACOTE qtd_lote
        FROM PCPC_040 l
        WHERE ({filtro_periodos_ocs})
          AND l.CODIGO_ESTAGIO = 63
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
