from pprint import pprint

from utils.functions.models import rows_to_dict_list


def posicao_get_op(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        , l.SITUACAO_ORDEM SITU
        , TO_CHAR(o.DATA_HORA, 'DD/MM/YYYY HH24:MI') DT
        , TO_CHAR(o.DATA_ENTRADA_CORTE, 'DD/MM/YYYY') DT_CORTE
        FROM PCPC_040 l
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = l.NOME_PROGRAMA_CRIACAO
         AND p.LOCALE = 'pt_BR'
        LEFT JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) != 0:
        situacoes = {
            1: 'ORDEM CONF. GERADA',
            2: 'ORDENS EM PRODUCAO',
            9: 'ORDEM CANCELADA',
        }
        for row in data:
            if row['SITU'] in situacoes:
                row['SITU'] = '{} - {}'.format(
                    row['SITU'], situacoes[row['SITU']])
    return data
