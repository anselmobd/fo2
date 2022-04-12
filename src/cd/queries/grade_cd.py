from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def lotes_em_estoque(cursor, get='ref'):

    if get == 'ref':
        distinct = True
        fields = """
              l.PROCONF_GRUPO ref
        """
    else:
        distinct = False
        fields = """
              l.PERIODO_PRODUCAO per
            , l.ORDEM_CONFECCAO oc
            , l.PROCONF_GRUPO ref
            , l.PROCONF_SUBGRUPO tam
            , tam.ORDEM_TAMANHO ordem_tam
            , l.PROCONF_ITEM cor
            , l.ORDEM_PRODUCAO op
            , l.QTDE_PECAS_PROG prog
            , l.QTDE_DISPONIVEL_BAIXA disp
        """

    sql = f"""
        SELECT {"DISTINCT" if distinct else ""}
        {fields}
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE l.CODIGO_ESTAGIO = 63
          AND l.QTDE_DISPONIVEL_BAIXA > 0
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
