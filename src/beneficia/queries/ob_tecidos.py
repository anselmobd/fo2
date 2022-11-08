import datetime
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, ob=None):

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
