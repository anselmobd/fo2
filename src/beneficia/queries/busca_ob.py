from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import split_non_empty, split_strip


def append_ordem_test(lista, comp, ordem):
    lista.append(" ".join(["b.ORDEM_PRODUCAO", comp, ordem]))


def query(
        cursor, ob=None, periodo=None, obs=None, ordens=None, ot=None, ob2=None, ref=None):

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
            AND UPPER(b.OBSERVACAO) LIKE UPPER('%{obs}%')
        """

    filtra_ordens = ""
    if ordens:
        filtro_list = []
        for chunk in split_non_empty(ordens, ','):
            if '-' in chunk:
                sub_list = []
                limits = split_strip(chunk, '-')
                if limits[0]:
                    append_ordem_test(sub_list, ">=", limits[0])
                if limits[1]:
                    append_ordem_test(sub_list, "<=", limits[1])
                if sub_list:
                    sub_filtro = " AND ".join(sub_list)
                    filtro_list.append(f"({sub_filtro})")
            else:    
                append_ordem_test(filtro_list, "=", chunk)
        filtro = " OR ".join(filtro_list)
        filtra_ordens = f"AND ({filtro})"

    filtra_ot = ""
    if ot is not None and ot != '':
        filtra_ot = f"""--
            AND b.ORDEM_TINGIMENTO = {ot}
        """

    filtra_ob2 = ""
    if ob2 is not None and ob2 != '':
        filtra_ob2 = f"""--
            AND bd.ORDEM_PRODUCAO = {ob2}
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
        , ( SELECT
              t.PANO_SBG_GRUPO
            FROM pcpb_020 t
            WHERE t.ORDEM_PRODUCAO = b.ORDEM_PRODUCAO
              AND rownum = 1
          ) REF
        , bd.ORDEM_PRODUCAO OB2
        FROM PCPB_010 b -- OB
        LEFT JOIN PCPT_050 canc
          ON canc.COD_CANCELAMENTO = b.COD_CANCELAMENTO 
        LEFT JOIN pcpb_030 bd -- destinos
          ON bd.PEDIDO_CORTE = 7 
         AND bd.NR_PEDIDO_ORDEM = b.ORDEM_PRODUCAO
        WHERE 1=1
          {filtra_ob} -- filtra_ob
          {filtra_periodo} -- filtra_periodo
          {filtra_obs} -- filtra_obs
          {filtra_ordens} -- filtra_ordens
          {filtra_ot} -- filtra_ot
          {filtra_ob2} -- filtra_ob2
          {filtra_ref} -- filtra_ref
        ORDER BY
          b.ORDEM_PRODUCAO
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['maq'] = f"{row['grup_maq']} {row['sub_maq']} {row['num_maq']:05}"
        if row['obs'] is None:
            row['obs'] = ''
        row['sit'] = f"{row['cod_sit']}-{row['descr_sit']}"
        if row['dt_canc'] is None:
            row['canc'] = '-'
        else:
            row['canc'] = f"{row['dt_canc'].date()} {row['cod_canc']:03}-{row['descr_canc']}"
        if row['ref'] is None:
            row['ref'] = ''


    return dados
