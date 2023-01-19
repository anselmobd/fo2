from pprint import pprint

from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from produto.functions import item_str

__all__ = ['query']


def query(
        cursor, rolo=None, sit=None, ref=None, cor=None, op=None,
        reserva_de=None, reserva_ate=None, est_res=None,
        est_aloc=None, est_conf=None):

    filtro_rolo = f"""--
        AND ro.CODIGO_ROLO = {rolo}
    """ if rolo else ''

    filtro_sit = f"""--
        AND ro.ROLO_ESTOQUE = {sit}
    """ if sit else ''

    filtro_ref = f"""--
        AND ro.PANOACAB_GRUPO = '{ref}'
    """ if ref else ''

    filtro_cor = f"""--
        AND ro.PANOACAB_ITEM = '{cor}'
    """ if cor else ''

    filtro_op = f"""--
        AND re.ORDEM_PRODUCAO = '{op}'
    """ if op else ''

    filtro_reserva_de = ''
    if reserva_de:
        est_res = 'S'
        filtro_reserva_de = f"""--
            AND re.DATA_RESERVA >= '{reserva_de}'
        """

    filtro_reserva_ate = ''
    if reserva_ate:
        est_res = 'S'
        filtro_reserva_ate = f"""--
            AND re.DATA_RESERVA <= '{reserva_ate}'
        """

    filtro_est_res = ''
    if est_res:
        null_res = "NOT" if est_res == 'S' else ''
        filtro_est_res = f"""--
            AND re.ORDEM_PRODUCAO IS {null_res} NULL
        """

    filtro_est_aloc = ''
    if est_aloc:
        null_aloc = "NOT" if est_aloc == 'S' else ''
        filtro_est_aloc = f"""--
            AND rc.ROLO_CONFIRMADO IS {null_aloc} NULL
        """

    filtro_est_conf = ''
    if est_conf:
        null_conf = "NOT" if est_conf == 'S' else ''
        filtro_est_conf = f"""--
            AND rc.DATA_HORA_CONF IS {null_conf} NULL
        """

    sql = f"""
        SELECT
          ro.CODIGO_ROLO rolo
        , ro.PANOACAB_NIVEL99 nivel
        , ro.PANOACAB_GRUPO ref
        , ro.PANOACAB_SUBGRUPO tam
        , ro.PANOACAB_ITEM cor
        , ro.PESO_BRUTO peso
        , ro.ROLO_ESTOQUE sit
        , ro.DATA_ENTRADA dt_entr
        , re.ORDEM_PRODUCAO op
        , re.DATA_RESERVA dt_reserva
        , re.USUARIO_RESERVA u_reserva 
        , rc.ROLO_CONFIRMADO conf
        , rc.ORDEM_PRODUCAO op_aloc
        , rc.DATA_HORA_CONF dh_conf
        , rc.USUARIO u_conf
        , ro.NOTA_FISCAL_ENT nf_num
        , ro.SERI_FISCAL_ENT nf_ser
        , ro.FORNECEDOR_CGC9 cnpj9
        , ro.FORNECEDOR_CGC4 cnpj4
        , ro.FORNECEDOR_CGC2 cnpj2
        , f.NOME_FORNECEDOR forn
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN TMRP_141 re -- reserva de rolo para OP
          ON re.CODIGO_ROLO = ro.CODIGO_ROLO
        LEFT JOIN PCPT_025 rc -- alocação de rolo para OP
          ON rc.CODIGO_ROLO = ro.CODIGO_ROLO
        LEFT JOIN SUPR_010 f -- fornecedor
          ON f.FORNECEDOR9 = ro.FORNECEDOR_CGC9
         AND f.FORNECEDOR4 = ro.FORNECEDOR_CGC4
         AND f.FORNECEDOR2 = ro.FORNECEDOR_CGC2
        WHERE 1=1
          {filtro_rolo} -- filtro_rolo
          {filtro_sit} -- filtro_sit
          {filtro_ref} -- filtro_ref
          {filtro_cor} -- filtro_cor
          {filtro_op} -- filtro_op
          {filtro_reserva_de} -- filtro_reserva_de
          {filtro_reserva_ate} -- filtro_reserva_ate
          {filtro_est_res} -- filtro_est_res
          {filtro_est_aloc} -- filtro_est_aloc
          {filtro_est_conf} -- filtro_est_conf
        ORDER BY
          ro.DATA_ENTRADA DESC
        , ro.CODIGO_ROLO DESC
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['forn_cnpj'] = format_cnpj(row) if row['cnpj9'] else '-'
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}" if row['nf_num'] else '-'
        row['item'] = item_str(row['nivel'], row['ref'], row['tam'], row['cor'])
    return data
