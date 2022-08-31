from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from cd.queries.novo_modulo import cd_lote_hist_duomo

__all__ = ['query']


__atividade = {
    1: "Colocando lote em palete",
    2: "Tirando lote de palete",
    3: "(Des)Endereçando palete",  # não utilizado em movimentos de lotes
}


def query(cursor, lote):

    hist_duomo = cd_lote_hist_duomo.query(cursor, lote)

    def get_hist_row(data_versao):
        for row in hist_duomo:
            if row['data_versao'] <= data_versao:
                return row

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
                hist_row = get_hist_row(row['data_hora'])
                row['sistema'] = 'Apoio'
                row['tela'] = 'Esvazia palete'
                if hist_row:
                    row['login'] = hist_row['usuario_systextil'] or '-'
                else:
                    row['login'] = '?'
            elif (
                row['usuario'].startswith('SYSTEXTIL/APEX:APP ')
            ):
                row['sistema'] = 'APEX'
        else:
            row['usuario'] = '-'

    return data
