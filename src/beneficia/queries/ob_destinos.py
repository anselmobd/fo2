from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from beneficia.queries import busca_ob


def query(cursor, ob=None):

    filtra_ob = ""
    if ob is not None and ob != '':
        filtra_ob = f"""--
            AND b.ORDEM_PRODUCAO = {ob}
        """

    sql = f'''
        SELECT 
          b.PEDIDO_CORTE
        , b.NR_PEDIDO_ORDEM NUMERO
        , b.CODIGO_DEPOSITO DEP
        , b.QTDE_ROLOS_PROG ROLOS
        , b.QTDE_QUILOS_PROG QUILOS
        FROM pcpb_030 b
        WHERE 1=1
          {filtra_ob} -- filtra_ob
        ORDER BY
          b.NR_PEDIDO_ORDEM
    '''

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    if dados:
        ob1_list = tuple([
            row['numero']
            for row in dados
            if row['numero'] != 0
        ])
        if ob1_list:
            dados_ob1_list = busca_ob.query(cursor, ob=ob1_list)
            dict_ob1 = {
                row['ob']: row
                for row in dados_ob1_list
            }

            for row in dados:
                ob1_row = dict_ob1.get(row['numero'])
                row['op'] = ob1_row['op']
  
    return dados
