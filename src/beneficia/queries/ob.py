import datetime
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def ob_estagios(cursor, ob=None):

    filtra_ob = ""
    if ob is not None and ob != '':
        filtra_ob = f"""--
            AND bt.ORDEM_PRODUCAO = {ob}
        """

    sql = f'''
        SELECT DISTINCT
          bt.SEQ_OPERACAO SEQ
        , bt.CODIGO_ESTAGIO EST
        , e.DESCRICAO EST_DESCR
        , bt.DATA_INICIO DT_INI
        , bt.HORA_INICIO H_INI
        , uini.USUARIO USUARIO_INI
        , bt.DATA_TERMINO DT_FIM
        , bt.HORA_TERMINO H_FIM
        , ufim.USUARIO USUARIO_FIM
        FROM pcpb_015 bt
        LEFT JOIN HDOC_030 uini -- usuários
          ON uini.CODIGO_USUARIO = bt.OPERADOR_INICIO 
        LEFT JOIN HDOC_030 ufim -- usuários
          ON ufim.CODIGO_USUARIO = bt.OPERADOR_TERMINO 
        LEFT JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = bt.CODIGO_ESTAGIO
        WHERE 1=1
          {filtra_ob} -- filtra_ob
        ORDER BY
          bt.SEQ_OPERACAO
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        if row['dt_ini']:
            row['ini'] = datetime.datetime.combine(
                row['dt_ini'].date(),
                row['h_ini'].time(),
            )
        else:
            row['ini'] = ''
        if not row['usuario_ini']:
            row['usuario_ini'] = ''
        if row['dt_fim']:
            row['fim'] = datetime.datetime.combine(
                row['dt_fim'].date(),
                row['h_fim'].time(),
            )
        else:
            row['fim'] = ''
        if not row['usuario_fim']:
            row['usuario_fim'] = ''

    return dados


def ob_tecidos(cursor, ob=None):

    filtra_ob = ""
    if ob is not None and ob != '':
        filtra_ob = f"""--
            AND b.ORDEM_PRODUCAO = {ob}
        """

    sql = f'''
        SELECT 
          b.PANO_SBG_NIVEL99 NIVEL
        , b.PANO_SBG_GRUPO REF
        , b.PANO_SBG_SUBGRUPO TAM
        , b.PANO_SBG_ITEM COR
        , b.ALTERNATIVA_ITEM ALT
        , b.ROTEIRO_OPCIONAL ROT
        , b.QTDE_ROLOS_PROG ROLOS_PROG
        , b.QTDE_QUILOS_PROG QUILOS_PROG
        , b.QTDE_ROLOS_REAL ROLOS_REAL
        , b.QTDE_QUILOS_REAL QUILOS_REAL
        , b.QTDE_ROLOS_PROD ROLOS_PROD
        , b.QTDE_QUILOS_PROD QUILOS_PROD
        FROM pcpb_020 b
        WHERE 1=1
          {filtra_ob} -- filtra_ob
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
