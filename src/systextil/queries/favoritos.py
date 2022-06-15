from pprint import pprint

from utils.functions.models import dictlist_lower


def query(cursor, empresa, usuario):
    sql = f"""
        SELECT
          up.PROGRAMA
        , p.DESCRICAO
        FROM HDOC_033 up -- usuário programa
        JOIN HDOC_035 p -- programas
          ON p.CODIGO_PROGRAMA = up.PROGRAMA
        WHERE 1=1
          AND up.NOME_MENU = 'favoritos'
          AND up.USU_PRG_EMPR_USU = {empresa}
          AND up.USU_PRG_CDUSU = '{usuario}'
    """
    print(sql)
    cursor.execute(sql)
    return dictlist_lower(cursor)
