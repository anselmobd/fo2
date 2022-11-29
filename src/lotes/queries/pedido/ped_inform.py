from pprint import pprint

from utils.functions.dict import dict_get_none
from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import (
    dictlist,
    dictlist_lower,
)
from utils.functions.queries import debug_cursor_execute

__all__ = ['ped_inform_lower', 'ped_inform']


_DICT_STATUS_PEDIDO = {
    None: {
        None: "Desconhecido",
        'tpl': '{k}-{v}',
    },
    0: 'Digitado',
    1: 'Financeiro',
    2: 'Liberado Financeiro',
    3: 'Faturamento',
    4: 'A cancelar',
    5: 'Cancelado',
    9: 'Aberto na web',
}

_DICT_SITUACAO_VENDA = {
    None: {
        None: "Desconhecido",
        'tpl': '{k}-{v}',
    },
    0: 'Pedido liberado',
    5: 'Pedido suspenso',
    10: 'Faturado total',
    15: 'Pedido com NF cancelada',
}

_DICT_EMPRESA = {    
    None: {
        None: "Desconhecida",
        'tpl': '{k}-{v}',
    },
    1: 'Tussor matriz',
    2: 'Agator',
    3: 'Tussor filial corte',
}


def ped_inform_lower(cursor, pedido, empresa=1, f_dictlist=dictlist_lower):
    return ped_inform(cursor, pedido, empresa, f_dictlist)


def ped_inform(cursor, pedido, empresa=1, f_dictlist=dictlist):
    if f_dictlist == dictlist:
        f_case = str.upper
    else:
        f_case = str.lower

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
        , c.FANTASIA_CLIENTE FANTASIA
        , c.CGC_9 CLIENTE_9
        , c.CGC_4 CLIENTE_4
        , c.CGC_2 CLIENTE_2
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , ped.STATUS_PEDIDO STATUS_PEDIDO_CODIGO
        , ped.COD_CANCELAMENTO
        , ped.COD_CANCELAMENTO
            || '-' || canc.DESC_CANC_PEDIDO
          CANCELAMENTO_DESCR
        , ped.SITUACAO_VENDA SITUACAO_VENDA_CODIGO
        , ped.CODIGO_EMPRESA
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
    data = f_dictlist(cursor)

    for row in data:
        row[f_case('STATUS_PEDIDO')] = dict_get_none(
            _DICT_STATUS_PEDIDO,
            row[f_case('STATUS_PEDIDO_CODIGO')],
        )
        row[f_case('SITUACAO_VENDA')] = dict_get_none(
            _DICT_SITUACAO_VENDA,
            row[f_case('SITUACAO_VENDA_CODIGO')],
        )
        row[f_case('EMPRESA')] = dict_get_none(
            _DICT_EMPRESA,
            row[f_case('CODIGO_EMPRESA')],
        )
        row[f_case('CNPJ')] = format_cnpj(row, contain=f_case('CLIENTE_'))
        cnpj = row[f_case('CNPJ')]
        nome_cliente = row[f_case('NOME_CLIENTE')]
        row[f_case('CLIENTE')] = f"{nome_cliente} ({cnpj})"

    return data
