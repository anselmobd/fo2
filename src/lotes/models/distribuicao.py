from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def distribuicao(cursor, estagio, data_de, data_ate, familia):
    sql = '''
        SELECT
          TO_CHAR(h.DATA_INSERCAO, 'YYYY/MM/DD') DATA_SORT
        , TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY') DATA
        , h.CODIGO_FAMILIA FAMILIA
        , count(DISTINCT h.ORDEM_PRODUCAO) OPS
        , count(*) LOTES
        , sum(h.QTDE_PRODUZIDA) PECAS
        FROM PCPC_045 h
        WHERE h.PCPC040_ESTCONF = %s
          AND TO_DATE(h.DATA_INSERCAO) >= %s
          AND TO_DATE(h.DATA_INSERCAO)-1 <= %s
          AND (-1 = %s OR h.CODIGO_FAMILIA = %s)
        GROUP BY
          TO_CHAR(h.DATA_INSERCAO, 'YYYY/MM/DD')
        , TO_CHAR(h.DATA_INSERCAO, 'DD/MM/YYYY')
        , h.CODIGO_FAMILIA
        ORDER BY
          1
        , h.CODIGO_FAMILIA
    '''
    cursor.execute(sql, [estagio, data_de, data_ate, familia, familia])
    return rows_to_dict_list(cursor)
