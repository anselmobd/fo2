from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, data):
    sql = f'''
    '''
    debug_cursor_execute(cursor, sql)
    dados = rows_to_dict_list_lower(cursor)
    clientes = {}
    for row in dados:
        if row['cliente'] not in clientes:
            clientes[row['cliente_slug']] = {
                'cliente': row['cliente'],
                'pedidos': {}
            }
            cliaux = clientes[row['cliente_slug']]['pedidos']
            if row['ped_cli'] not in cliaux:
                cliaux[row['ped_cli']] = {row['op']}
            else:
                cliaux[row['ped_cli']].add(row['op'])

    return dados, clientes