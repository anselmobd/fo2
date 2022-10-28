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

__apex_tela = {
    '49': "duom_fa01",
    '50': "duom_fa02",
    '51': "duom_fa03",
    '52': "duom_fa04",
    '53': "duom_fa05",
    '54': "duom_fa06",
    '55': "duom_fa07",
    '56': "duom_fa08",
    '57': "duom_fa09",
    '58': "duom_fa10",
    '59': "duom_fa11",
    '60': "duom_fa12",
    '61': "duom_fa13",
    '62': "duom_fa14",
    '63': "duom_fa15",
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
        , u.USUARIO USUARIO_SYSTEXTIL
        FROM ENDR_016_HIST h -- histórico de endereçamento
        LEFT JOIN HDOC_030 u -- usuários
          ON u.EMPRESA = 1
         AND u.USUARIO = h.USUARIO 
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
                try:
                    pagina = row['usuario'].split()[1].split(':')[1]
                    row['tela'] = __apex_tela[pagina]
                except Exception:
                    pass
            elif row['usuario_systextil']:
                row['login'] = row['usuario_systextil']
        else:
            row['usuario'] = '-'

    return data
