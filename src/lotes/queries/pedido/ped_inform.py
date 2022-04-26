from pprint import pprint

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import debug_cursor_execute


def ped_inform(cursor, pedido, empresa=1):

    filtro_empresa = ""
    if empresa:
        if not isinstance(empresa, tuple):
            empresa = (empresa, )
        empresas_list = []
        for empr in empresa:
            if empr:
                empresas_list.append(f"ped.CODIGO_EMPRESA = {empr}")
        filtro_empresa = f"""--
            AND ({' OR '.join(empresas_list)})
        """

    if not isinstance(pedido, tuple):
        pedido = (pedido, )
    pedido_list = []
    for ped in pedido:
        if ped:
            pedido_list.append(f"ped.PEDIDO_VENDA = {ped}")
    filtro_pedido = f"""--
        AND ({' OR '.join(pedido_list)})
    """
    sql = f"""
        SELECT
          ped.PEDIDO_VENDA
        , COALESCE(
            ( SELECT
                LISTAGG(i.CODIGO_DEPOSITO, ', ')
                WITHIN GROUP (ORDER BY i.CODIGO_DEPOSITO)
              FROM (
                SELECT DISTINCT
                  ii.CODIGO_DEPOSITO
                , ii.PEDIDO_VENDA
                FROM PEDI_110 ii
              ) i
              WHERE i.PEDIDO_VENDA = ped.PEDIDO_VENDA
            )
          , ' '
          ) DEPOSITO
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , ped.DATA_ENTR_VENDA DT_EMBARQUE
        , ped.OBSERVACAO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , c.CGC_9 CLIENTE_9
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , ped.STATUS_PEDIDO STATUS_PEDIDO_CODIGO
        , CASE ped.STATUS_PEDIDO
          WHEN 0 THEN '0-Digitado'
          WHEN 1 THEN '1-Financeiro'
          WHEN 2 THEN '2-Liberado Financeiro'
          WHEN 3 THEN '3-Faturamento'
          WHEN 4 THEN '4-A cancelar'
          WHEN 5 THEN '5-Cancelado'
          WHEN 9 THEN '9-Aberto na web'
          END STATUS_PEDIDO
        , ped.COD_CANCELAMENTO
        , ped.COD_CANCELAMENTO
            || '-' || canc.DESC_CANC_PEDIDO
          CANCELAMENTO_DESCR
        , CASE ped.SITUACAO_VENDA
          WHEN 0  THEN '0-Pedido liberado'
          WHEN 5  THEN '5-Pedido suspenso'
          WHEN 10 THEN '10-Faturado total'
          WHEN 15 THEN '15-Pedido com NF cancelada'
          END SITUACAO_VENDA
        , ped.CODIGO_EMPRESA
        , CASE ped.CODIGO_EMPRESA
          WHEN 1 THEN '1-Tussor matriz'
          WHEN 2 THEN '2-Agator'
          WHEN 3 THEN '3-Tussor filial corte'
          END EMPRESA
        , ( SELECT
              f.NUM_NOTA_FISCAL 
            FROM FATU_050 f
            LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
              ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
             AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada 
            WHERE f.PEDIDO_VENDA = ped.PEDIDO_VENDA
              AND f.SITUACAO_NFISC = 1
              AND fe.SITUACAO_ENTRADA IS NULL
          ) NF
        FROM PEDI_100 ped -- pedido de venda
        JOIN PEDI_140 canc -- código de cancelamento
          ON canc.COD_CANC_PEDIDO = ped.COD_CANCELAMENTO
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE 1=1
          {filtro_pedido} -- filtro_pedido
          {filtro_empresa} -- filtro_empresa
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list(cursor)
