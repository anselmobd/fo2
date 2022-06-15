from pprint import pprint

from utils.functions.models import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = """
        SELECT
          di.DIVISAO_PRODUCAO DIV
        , di.DESCRICAO DESCR
        , ci.ESTADO UF
        , ci.CIDADE
        , ' (' || lpad(fo.FORNECEDOR9, 8, '0')
          || '/' || lpad(fo.FORNECEDOR4, 4, '0')
          || '-' || lpad(fo.FORNECEDOR2, 2, '0')
          || ') '
          || fo.NOME_FORNECEDOR NOME
        FROM BASI_180 di -- divisão / unidade
        JOIN SUPR_010 fo -- fornacedor
          ON fo.FORNECEDOR9 = di.FACCIONISTA9
         AND fo.FORNECEDOR4 = di.FACCIONISTA4
         AND fo.FORNECEDOR2 = di.FACCIONISTA2
        JOIN BASI_160 ci -- cidade
          ON ci.COD_CIDADE = fo.COD_CIDADE
        WHERE di.DIVISAO_PRODUCAO > 1
          AND di.DIVISAO_PRODUCAO < 1000
        ORDER BY
          di.DIVISAO_PRODUCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
