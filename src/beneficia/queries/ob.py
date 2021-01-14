from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def busca_ob(cursor, ob=None, periodo=None, obs=None):
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

    filtra_obs = ""
    if obs is not None and obs != '':
        filtra_obs = f"""--
            AND b.OBSERVACAO LIKE '%{obs}%'
        """

    sql = f'''
        SELECT 
          b.ORDEM_PRODUCAO OB
        , b.PERIODO_PRODUCAO PERIODO
        , b.GRUPO_MAQUINA GRUP_MAQ
        , b.SUBGRUPO_MAQUINA SUB_MAQ 
        , b.NUMERO_MAQUINA NUM_MAQ
        , b.QTDE_ROLOS_PROG ROLOS
        , b.QTDE_QUILOS_PROG QUILOS
        , b.SITUACAO_ORDEM COD_SIT
        , b.OBSERVACAO OBS
        , CASE
            WHEN b.SITUACAO_ORDEM = 0 THEN 'A Emitir'
            WHEN b.SITUACAO_ORDEM = 1 THEN 'Emitida'
            ELSE '-'
          END DESCR_SIT
        , b.COD_CANCELAMENTO COD_CANC
        , b.DT_CANCELAMENTO DT_CANC
        , canc.DESCRICAO DESCR_CANC 
        , b.ORDEM_TINGIMENTO OT
        FROM PCPB_010 b
        LEFT JOIN PCPT_050 canc
          ON canc.COD_CANCELAMENTO = b.COD_CANCELAMENTO 
        WHERE 1=1
          {filtra_ob} -- filtra_ob
          {filtra_periodo} -- filtra_periodo
          {filtra_obs} -- filtra_obs
        ORDER BY
          b.ORDEM_PRODUCAO
    '''

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    for row in dados:
        row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"
        if row['obs'] is None:
            row['obs'] = ''
        row['sit'] = f"{row['cod_sit']}-{row['descr_sit']}"
        if row['dt_canc'] is None:
            row['canc'] = '-'
        else:
            row['canc'] = f"{row['dt_canc'].date()} {row['cod_canc']:03}-{row['descr_canc']}"

    return dados
