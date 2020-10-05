from pprint import pprint

from utils.functions.models import rows_to_dict_list


def posicao_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          el.CODIGO_ESTAGIO
        , el.DESCRICAO DESCRICAO_ESTAGIO
        FROM (
        SELECT
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND l.QTDE_EM_PRODUCAO_PACOTE <> 0
        UNION
        SELECT
          0
        , 'FINALIZADO'
        from dual
        ORDER BY
          1 DESC
        ) el
        WHERE rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)
