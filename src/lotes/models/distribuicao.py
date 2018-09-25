from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def distribuicao(cursor, estagio, data_de, data_ate, familia):
    sql = '''
        SELECT
          TO_CHAR(h.DATA_INSERCAO, 'YYYY/MM/DD') DATA_SORT
        , TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY') DATA
        , h.CODIGO_FAMILIA FAMILIA
        , h.ORDEM_PRODUCAO OP
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        --, count(DISTINCT h.ORDEM_PRODUCAO) OPS
        , count(*) LOTES
        , sum(h.QTDE_PRODUZIDA) PECAS
        FROM PCPC_045 h
        JOIN pcpc_040 l
          ON l.PERIODO_PRODUCAO = h.PCPC040_PERCONF
         AND l.ORDEM_CONFECCAO = h.PCPC040_ORDCONF
         AND l.CODIGO_ESTAGIO = h.PCPC040_ESTCONF
        WHERE h.PCPC040_ESTCONF = %s
          AND TO_DATE(h.DATA_INSERCAO) >= %s
          AND TO_DATE(h.DATA_INSERCAO)-1 <= %s
          AND (-1 = %s OR h.CODIGO_FAMILIA = %s)
        GROUP BY
          TO_CHAR(h.DATA_INSERCAO, 'YYYY/MM/DD')
        , TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY')
        , h.CODIGO_FAMILIA
        , h.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        ORDER BY
          1
        , h.CODIGO_FAMILIA
        , h.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
    '''
    cursor.execute(sql, [estagio, data_de, data_ate, familia, familia])
    return rows_to_dict_list(cursor)
