import re
from pprint import pprint

from django.utils.text import slugify

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__=['pedidos_filial_na_data']


def pedidos_filial_na_data(cursor, data=None, fantasia=None, op=None):
    """Busca pedidos auxiliares para faturamento de produção da filial
    Filtros
    - data: data do pedido (data de finalização do estágio 15 das OPs)
    - fansatia: nome fantasia do cliente do pedido da OP ou "estque"
        em caso de OP de estoque
    - op: OP produzida na filial
    Retorno
    - caso filtre por fantasia:
        retorna um dictlist com os dados dos pedidos filtrados daquele 
        cliente (ou estoque)
    - caso Não filtre por fantasia:
        retorna um dict com chave cliente (ou estoque) e valor dictlist
        com seus dados dos pedidos filtrados
    """
    if fantasia:
        slug_fantasia =  slugify(fantasia)

    if op:
        if not isinstance(op, (list, tuple)):
            op = [op]

    filtra_data = f"""--
        AND p.DATA_EMIS_VENDA = DATE '{data}'
        AND p.DATA_ENTR_VENDA = DATE '{data}'
    """ if data else ''

    sql = f"""
        SELECT
          p.PEDIDO_VENDA ped
        , p.OBSERVACAO obs
        , p.DATA_EMIS_VENDA data
        , f.NUM_NOTA_FISCAL nf
        FROM PEDI_100 p
        LEFT JOIN FATU_050 f
          ON f.PEDIDO_VENDA = p.PEDIDO_VENDA
        WHERE 1=1
          AND p.CODIGO_EMPRESA = 3
          AND p.COD_CANCELAMENTO = 0
          {filtra_data} -- filtra_data
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    peds = {}
    for row in dados:
        # obs = row.pop('obs')
        obs = row['obs']
        if not obs:
            continue
        if not re.search('^\[MPCFM\] ', obs):
            continue
        if data and not re.search(f"Data: {data}", obs):
            continue
        if re.search("Producao para estoque:", obs):
            cliente = 'estoque'
        else:
            cliente_match = re.search('Producao para o cliente ([^ ]+):', obs)
            if not cliente_match:
                continue
            cliente = cliente_match.group(1).lower()

        if fantasia:
            if not (
                cliente.upper().startswith(slug_fantasia.upper())
                or slug_fantasia.upper().startswith(cliente.upper())
            ):
                continue
            cliente = fantasia

        ped_op_pattern = re.compile(r'Pedido\(([0123456789-]+)\)-OP\(([0123456789, ]+)\)')
        match = ped_op_pattern.findall(obs)
        op_ped = {}
        for ped, str_ops in match:
            ops = str_ops.split(', ')
            for op1 in ops:
                op_ped[op1] = ped

        if op:
            achou = False
            for op1 in op:
                achou = achou or (op1 in op_ped)
            if not achou:
                continue

        row['op_ped'] = op_ped
        try:
            peds[cliente].append(row)
        except KeyError:
            peds[cliente] = [row]

    if fantasia and peds:
        return peds[fantasia]
    else:
        return peds
