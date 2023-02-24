from pprint import pprint

from django.utils.text import slugify

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, op, cliente_slug=None):
    """Busca informações de pedido e cliente de OP
    Parametro:
        op - uma OP ou uma lista de OPs
    Retorno:
        dictlist
    """
    
    if isinstance(op, (tuple, list)):
        ops = ", ".join(map(str, op))
        condicao = f"IN ({ops})"
    else:
        condicao = f"= {op}"
    filtra_op = f"""--
        AND op.ORDEM_PRODUCAO {condicao}
    """

    sql = f"""
        SELECT
          op.ORDEM_PRODUCAO OP
        , op.PEDIDO_VENDA ped
        , ped.COD_PED_CLIENTE PED_CLI
        , cli.FANTASIA_CLIENTE
        , cli.NOME_CLIENTE
        , CASE
            WHEN op.PEDIDO_VENDA = 0 THEN
              'ESTOQUE' 
            ELSE
              COALESCE(cli.FANTASIA_CLIENTE, cli.NOME_CLIENTE)
          END CLIENTE
        , cli.CGC_9
        , cli.CGC_4
        , cli.CGC_2
        FROM pcpc_020 op
        LEFT JOIN PEDI_100 ped
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 cli
          ON cli.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND cli.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND cli.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE 1=1
          {filtra_op} -- filtra_op
        ORDER BY 
          op.ORDEM_PRODUCAO
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        if not row['ped']:
            row['ped'] = '-'
        if not row['ped_cli']:
            row['ped_cli'] = '-'
        row['cliente_slug'] = slugify(row['cliente'])

    if cliente_slug:
        dados = [
            row
            for row in dados
            if row['cliente_slug'] == cliente_slug
        ]

    return dados
