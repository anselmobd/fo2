import re
from pprint import pprint

from django.core.cache import cache
from django.utils.text import slugify

from utils.cache import timeout
from utils.functions import (
    fo2logger,
    my_make_key_cache,
)
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__=['pedidos_filial_na_data']


def pedidos_filial_na_data_base(cursor, data=None, data_de=None):
    """Busca pedidos auxiliares para faturamento de produção da filial

    Filtros
    - data: data do pedido (data de finalização do estágio 16 das OPs)
    """

    key_cache = my_make_key_cache(
        'lotes/quer/ped/ped_filial/p_f_data_base',
        data,
        data_de,
    )
    dados = cache.get(key_cache)
    if dados:
        fo2logger.info('cached '+key_cache)
        return dados


    filtra_data = f"""--
        AND p.DATA_EMIS_VENDA = DATE '{data}'
    """ if data else ''

    filtra_data_de = f"""--
        AND p.DATA_EMIS_VENDA >= DATE '{data_de}'
    """ if data_de else ''

    sql = f"""
        SELECT
          p.PEDIDO_VENDA ped
        , p.OBSERVACAO obs
        , p.DATA_EMIS_VENDA data
        , f.NUM_NOTA_FISCAL nf
        , f.DATA_AUTORIZACAO_NFE nf_data
        , f.SITUACAO_NFISC situacao
        , f.CODIGO_EMPRESA nf_empresa
        , fe.DOCUMENTO nf_devolucao
        FROM PEDI_100 p
        LEFT JOIN FATU_050 f
          ON f.PEDIDO_VENDA = p.PEDIDO_VENDA
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
        WHERE 1=1
          AND p.CODIGO_EMPRESA = 3
          AND p.COD_CANCELAMENTO = 0
          {filtra_data} -- filtra_data
          {filtra_data_de} -- filtra_data_de
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['situacao_descr'] = None
        if row['situacao'] == 1:
            row['situacao_descr'] = 'Ativa'
        else:
            row['situacao_descr'] = 'Cancelada'

        if row['nf_devolucao'] is None:
            row['nf_devolucao'] = '-'
        else:
            row['situacao_descr'] += '/Devolvida'

    cache.set(key_cache, dados, timeout=timeout.MINUTE)
    fo2logger.info('calculated '+key_cache)

    return dados

def pedidos_filial_na_data(
    cursor,
    data=None,
    data_de=None,
    fantasia=None,
    op=None,
    pedido_cliente=None,
):
    """Busca pedidos auxiliares para faturamento de produção da filial

    Filtros
    - data: data do pedido (data de finalização do estágio 15 das OPs)
    - data_de: data do pedido mínima
    - fantasia: nome fantasia do cliente do pedido da OP ou "estoque"
        em caso de OP de estoque
    - op: OP produzida na filial
    - pedido_cliente: código de pedido do cliente

    Retorno
    - caso filtre por fantasia:
        retorna um dictlist com os dados dos pedidos filtrados daquele 
        cliente (ou estoque)
    - caso Não filtre por fantasia:
        retorna um dict com chave cliente (ou estoque) e valor dictlist
        com seus dados dos pedidos filtrados
    """

    dados = pedidos_filial_na_data_base(cursor, data=data, data_de=data_de)

    if fantasia:
        slug_fantasia =  slugify(fantasia)

    if op:
        if not isinstance(op, (list, tuple)):
            op = [op]

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

        if pedido_cliente:
            if pedido_cliente not in op_ped.values():
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
