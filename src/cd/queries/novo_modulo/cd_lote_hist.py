from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.views import data_url_image

__all__ = ['query']


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
        row['usuario_db'] = row['usuario']
        if row['usuario']:
            if (
                row['usuario'].startswith('WsAssociaca ')
                or row['usuario'].startswith('WS Associaca ')
            ):
                row['usuario'] = row['usuario'].split("-")[1]
                row['tela'] = 'endr_f015'
                row['sistema'] = 'Systextil'
                continue
            if (
                row['usuario'].startswith('python3@intranet ')
            ):
                row['usuario'] = '-'
                row['tela'] = 'Esvazia palete'
                row['sistema'] = 'Apoio'
                continue
            if (
                row['usuario'].startswith('SYSTEXTIL/APEX:APP ')
            ):
                row['usuario'] = '?'
                row['tela'] = '?'
                row['sistema'] = 'APEX'
                continue
        row['tela'] = '?'
        row['sistema'] = '?'
               
    return data
