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
        , CASE
            WHEN t.TIPO_ORDEM = 1 THEN '1 - Ordem tingimento'
            WHEN t.TIPO_ORDEM = 2 THEN '2 - Ordem lavação'
            WHEN t.TIPO_ORDEM = 3 THEN '3 - Ordem estamparia'
            WHEN t.TIPO_ORDEM = 4 THEN '4 - Ordem reprocesso'
            WHEN t.TIPO_ORDEM = 5 THEN '5 - Ordem retração'
            WHEN t.TIPO_ORDEM = 6 THEN '6 - Processo contínuo'
            WHEN t.TIPO_ORDEM = 7 THEN '7 - Ordem revestimento'
          ELSE ''
          END TIPO
        , t.RELACAO_BANHO 
        , t.VOLUME_BANHO 
        , t.GRUPO_MAQUINA GRUP_MAQ
        , t.SUBGRUPO_MAQUINA SUB_MAQ 
        , t.NUMERO_MAQUINA NUM_MAQ
        FROM PCPB_110 t -- OT
        WHERE 1=1
          {filtra_ot} -- filtra_ot
        ORDER BY
          t.ORDEM_AGRUPAMENTO
    '''

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    for row in dados:
        row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"

    return dados
