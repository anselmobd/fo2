from collections import OrderedDict
from pprint import pprint

from django.core.cache import cache

from utils.cache import timeout
from utils.functions import (
    fo2logger,
    my_make_key_cache_slug,
)

from lotes.models.op import OpCortada
from lotes.queries.op import (
    op_itens,
    op_ped_cli,
)

__all__ = ['mount', 'mount_all_and_cache', 'get_cached']


def ped_cli_por_cliente(pedidos_ops, itens_ops):
    # Separa OPs por clientes e pedidos
    clientes = {}
    for pedido_op in pedidos_ops:
        slug = pedido_op['cliente_slug']
        if slug not in clientes:
            clientes[slug] = {
                'cliente': pedido_op['cliente'],
                'pedidos': {},
                'ops': set(),
            }
        pedidos_do_cliente = clientes[slug]['pedidos']
        if pedido_op['ped_cli'] not in pedidos_do_cliente:
            pedidos_do_cliente[pedido_op['ped_cli']] = {pedido_op['op']}
        else:
            pedidos_do_cliente[pedido_op['ped_cli']].add(pedido_op['op'])
        clientes[slug]['ops'].add(pedido_op['op'])
    # Monta dados para pedido de faturamento filial-matriz
    for cli in clientes:
        cli_dict = clientes[cli]
        # Monta observação
        if cli == 'estoque':
            ops = ', '.join(map(str, cli_dict['pedidos']['-']))
            cli_dict['obs'] = f"OP({ops})"
        else:
            cli_dict['obs'] = ''
            sep = ''
            for ped in cli_dict['pedidos']:
                ops = ', '.join(map(str, cli_dict['pedidos'][ped]))
                cli_dict['obs'] += sep + f"Pedido({ped})-OP({ops})"
                sep = ', '
        # Monta itens
        itens_ops_cli = [
            item_ops
            for item_ops in itens_ops
            if item_ops['op'] in cli_dict['ops']
        ]
        cli_dict['itens'] = OrderedDict()
        for item_op in itens_ops_cli:
            try:
                cli_dict['itens'][item_op['item']] += item_op['qtd']
            except KeyError:
                cli_dict['itens'][item_op['item']] = item_op['qtd']
    return clientes


def mount(cursor, dt, cliente_slug=None, get_cached=False, or_calculate=False):
    """
    Monta informações para pedidos para NF filial-matriz
    em dict por cliente_slug
    """
    
    key_cache = my_make_key_cache_slug(
        'lotes/queries/op/ped_cli_por_cliente/mount',
        dt, cliente_slug,
    )
    if get_cached:
        dados = cache.get(key_cache)
        if dados:
            fo2logger.info('cached '+key_cache)
            if cliente_slug:
                dados = {
                    cliente: dados[cliente]
                    for cliente in dados
                    if cliente == cliente_slug
                }
            return dados
        else:
            if not or_calculate:
                return {}

    dados_ops = OpCortada.objects.filter(when__date__lte=dt)
    dados_ops = dados_ops.values()
    ops = [
        row['op']
        for row in dados_ops
    ]

    ped_cli_ops = op_ped_cli.query(cursor, op=ops, cliente_slug=cliente_slug)

    ops = [
        row['op']
        for row in ped_cli_ops
    ]

    itens_ops = op_itens.query(cursor, op=ops)

    dados = ped_cli_por_cliente(ped_cli_ops, itens_ops)

    cache.set(key_cache, dados, timeout=timeout.HOUR)
    fo2logger.info('calculated '+key_cache)

    return dados


def mount_all_and_cache(cursor, dt):
    return mount(cursor, dt)


def get_cached(cursor, dt, cliente_slug=None):
    return mount(cursor, dt, cliente_slug=cliente_slug, get_cached=True)
