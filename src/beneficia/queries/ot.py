import datetime
from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.strings import split_nonempty


def busca_ot(cursor, ot=None):

    filtra_ot = ""
    if ot is not None and ot != '':
        filtra_ot = f"""--
            AND t.ORDEM_AGRUPAMENTO = {ot}
        """

    sql = f'''
        SELECT 
          t.ORDEM_AGRUPAMENTO OT
        , t.ORDEM_PRODUCAO OB
        FROM PCPB_110 t -- OT
        WHERE 1=1
          {filtra_ot} -- filtra_ot
        ORDER BY
          t.ORDEM_AGRUPAMENTO
    '''

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    return dados
