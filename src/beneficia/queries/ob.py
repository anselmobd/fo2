import datetime
from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def busca_ob(cursor, ob=None, periodo=None, obs=None, ot=None, ref=None):

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

    filtra_ot = ""
    if ot is not None and ot != '':
        filtra_ot = f"""--
            AND b.ORDEM_TINGIMENTO = {ot}
        """

    filtra_ref = ""
    if ref is not None and ref != '':
        filtra_ref = f"""--
            AND EXISTS (
                SELECT DISTINCT 
                t.ORDEM_PRODUCAO
                FROM pcpb_020 t
                WHERE t.ORDEM_PRODUCAO = b.ORDEM_PRODUCAO
                AND t.PANO_SBG_GRUPO = '{ref}'
            )
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
          {filtra_ot} -- filtra_ot
          {filtra_ref} -- filtra_ref
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


def ob_estagios(cursor, ob=None):

    filtra_ob = ""
    if ob is not None and ob != '':
        filtra_ob = f"""--
            AND bt.ORDEM_PRODUCAO = {ob}
        """

    sql = f'''
        SELECT 
          bt.SEQ_OPERACAO SEQ
        , bt.CODIGO_ESTAGIO EST
        , bt.DATA_INICIO DT_INI
        , bt.HORA_INICIO H_INI
        , bt.DATA_TERMINO DT_FIM
        , bt.HORA_TERMINO H_FIM
        FROM pcpb_015 bt
        WHERE 1=1
          {filtra_ob} -- filtra_ob
    '''

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    for row in dados:
        row['ini'] = datetime.datetime.combine(
            row['dt_ini'].date(),
            row['h_ini'].time(),
        )
        row['fim'] = datetime.datetime.combine(
            row['dt_fim'].date(),
            row['h_fim'].time(),
        )

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

    cursor.execute(sql)
    dados = rows_to_dict_list_lower(cursor)

    return dados
