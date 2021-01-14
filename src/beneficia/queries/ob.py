from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def busca_ob(cursor, ob=None, periodo=None):
    filtra_ob = ""
    if ob is not None and ob != '':
        filtra_ob = f"""--
            AND b.ORDEM_PRODUCAO = {ob}
        """

    filtra_periodo = ""
    if periodo is not None and periodo != '':
        filtra_periodo = f"""--
            AND b.PERIODO_PRODUCAO = {periodo}
        """

    sql = f'''
        SELECT 
          b.ORDEM_PRODUCAO OB
        , b.PERIODO_PRODUCAO PERIODO
        , b.GRUPO_MAQUINA GRUP_MAQ
        , b.SUBGRUPO_MAQUINA SUB_MAQ 
        , b.ORDEM_TINGIMENTO OT
        FROM PCPB_010 b
        WHERE 1=1
          {filtra_ob} -- filtra_ob
          {filtra_periodo} -- filtra_periodo
    '''

    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
