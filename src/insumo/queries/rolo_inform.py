from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(
        cursor, rolo=None, sit=None, ref=None, cor=None, op=None,
        reserva_de=None, reserva_ate=None, est_res=None,
        est_aloc=None, est_conf=None):

    filtro_rolo = ''
    if rolo is not None and rolo != '':
      filtro_rolo = f"""--
          AND ro.CODIGO_ROLO = {rolo}
      """

    filtro_sit = ''
    if sit is not None and sit != '':
      filtro_sit = f"""--
          AND ro.ROLO_ESTOQUE = {sit}
      """

    filtro_ref = ''
    if ref is not None and ref != '':
      filtro_ref = f"""--
          AND ro.PANOACAB_GRUPO = '{ref}'
      """

    filtro_cor = ''
    if cor is not None and cor != '':
      filtro_cor = f"""--
          AND ro.PANOACAB_ITEM = '{cor}'
      """

    filtro_op = ''
    if op is not None and op != '':
      filtro_op = f"""--
          AND re.ORDEM_PRODUCAO = '{op}'
      """

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
    if est_res is not None:
      if est_res == 'S':
        filtro_est_res = """--
            AND re.ORDEM_PRODUCAO IS NOT NULL
        """
      elif est_res == 'N':
        filtro_est_res = """--
            AND re.ORDEM_PRODUCAO IS NULL
        """

    filtro_est_aloc = ''
    if est_aloc is not None:
      if est_aloc == 'S':
        filtro_est_aloc = """--
            AND rc.ROLO_CONFIRMADO IS NOT NULL
        """
      elif est_aloc == 'N':
        filtro_est_aloc = """--
            AND rc.ROLO_CONFIRMADO IS NULL
        """

    filtro_est_conf = ''
    if est_conf is not None:
      if est_conf == 'S':
        filtro_est_conf = """--
            AND rc.DATA_HORA_CONF IS NOT NULL
        """
      elif est_conf == 'N':
        filtro_est_conf = """--
            AND rc.DATA_HORA_CONF IS NULL
        """

    sql = f"""
        SELECT
          ro.CODIGO_ROLO rolo
        , ro.PANOACAB_NIVEL99 nivel
        , ro.PANOACAB_GRUPO ref
        , ro.PANOACAB_SUBGRUPO tam
        , ro.PANOACAB_ITEM cor
        , ro.ROLO_ESTOQUE sit
        , ro.DATA_ENTRADA dt_entr
        , re.ORDEM_PRODUCAO op
        , re.DATA_RESERVA dt_reserva
        , re.USUARIO_RESERVA u_reserva 
        , rc.ROLO_CONFIRMADO conf
        , rc.ORDEM_PRODUCAO op_aloc
        , rc.DATA_HORA_CONF dh_conf
        , rc.USUARIO u_conf
        , ro.NOTA_FISCAL_ENT nf
        , ro.SERI_FISCAL_ENT nf_ser
        , ro.FORNECEDOR_CGC9 forn9
        , ro.FORNECEDOR_CGC4 forn4
        , ro.FORNECEDOR_CGC2 forn2
        , f.NOME_FORNECEDOR forn
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN TMRP_141 re -- reserva de rolo para OP
          ON re.CODIGO_ROLO = ro.CODIGO_ROLO
        LEFT JOIN PCPT_025 rc
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
    return dictlist(cursor)
