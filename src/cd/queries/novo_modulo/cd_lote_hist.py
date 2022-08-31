from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.views import data_url_image

__all__ = ['query']


__atividade = {
    1: "Colocando lote em palete",
    2: "Tirando lote de palete",
    3: "(Des)Endereçando palete",  # não utilizado em movimentos de lotes
}


def query(cursor, lote):
    sql = f"""
        SELECT
          h.USUARIO
        , h.DATA_HORA
        , h.ATIVIDADE
        , h.COD_CONTAINER
        , h.ENDERECO
        , h.ORDEM_PRODUCAO
        , h.ORDEM_CONFECCAO
        FROM ENDR_016_HIST h
        WHERE h.ORDEM_CONFECCAO = {lote}
        ORDER BY 
          h.DATA_HORA DESC 
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['atividade'] = __atividade[row['atividade']]
        if row['endereco'] is None:
            row['endereco'] = '-'
        row['sistema'] = '?'
        row['tela'] = '?'
        row['login'] = '?'
        if row['usuario']:
            if (
                row['usuario'].startswith('WsAssociaca ')
                or row['usuario'].startswith('WS Associaca ')
            ):
                row['sistema'] = 'Systextil'
                row['tela'] = 'endr_f015'
                row['login'] = row['usuario'].split("-")[1]
            elif (
                row['usuario'].startswith('python3@intranet ')
            ):
                row['sistema'] = 'Apoio'
                row['tela'] = 'Esvazia palete'
                row['login'] = '-'
            elif (
                row['usuario'].startswith('SYSTEXTIL/APEX:APP ')
            ):
                row['sistema'] = 'APEX'
        else:
            row['usuario'] = '-'

    return data
