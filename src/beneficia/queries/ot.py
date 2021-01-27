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
        , t.TIPO_ORDEM
        , t.RELACAO_BANHO 
        , t.VOLUME_BANHO 
        , t.GRUPO_MAQUINA GRUP_MAQ
        , t.SUBGRUPO_MAQUINA SUB_MAQ 
        , t.NUMERO_MAQUINA NUM_MAQ
        , t.SITUACAO
        FROM PCPB_100 t -- OT
        WHERE 1=1
          {filtra_ot} -- filtra_ot
        ORDER BY
          t.ORDEM_AGRUPAMENTO
    '''

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    tipo_ordem = {
        '1': '1-Ordem tingimento',
        '2': '2-Ordem lavação',
        '3': '3-Ordem estamparia',
        '4': '4-Ordem reprocesso',
        '5': '5-Ordem retração',
        '6': '6-Processo contínuo',
        '7': '7-Ordem revestimento',
        '': '-',
    }

    situacao = {
        '0': '0-Digitada',
        '1': '1-Impressa',
        '2': '2-A produzir',
        '3': '3-Em producao',
        '4': '4-Produzida',
        '5': '5-Ordem alterada na producao',
        '': '-',
    }

    for row in dados:
        row['tipo'] = tipo_ordem[row['tipo_ordem']]
        row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"
        row['sit'] = situacao[row['situacao']]

    return dados
