from pprint import pprint

from utils.functions.models import rows_to_dict_list, rows_to_dict_list_lower


def deposito(cursor, only=None, less=None):

    def monta_filtro(in_, depositos):
        filtro = ''
        if depositos is not None:
            lista_depositos = ''
            sep = ''
            for deposito in depositos:
                    lista_depositos += f'{sep}{str(deposito)}'
                    sep = ', '
            filtro = (
                f'AND d.CODIGO_DEPOSITO {in_} ({lista_depositos})')
        return filtro

    filtra_depositos = ' '.join([
        monta_filtro('IN', only),
        monta_filtro('NOT IN', less),
    ])

    sql = f'''
        SELECT
          d.CODIGO_DEPOSITO COD
        , d.DESCRICAO DESCR
        , d.TIP_PROPRIEDADE_DEPOSITO PROP
        , d.CNPJ9
        , d.CNPJ4
        , d.CNPJ2
        , CASE WHEN d.CNPJ9 = 0 THEN ' '
          ELSE coalesce(coalesce(f.NOME_FANTASIA, f.NOME_FORNECEDOR), '#')
          END FORN
        FROM BASI_205 d
        LEFT JOIN SUPR_010 f
          ON f.FORNECEDOR9 = d.CNPJ9
         AND f.FORNECEDOR4 = d.CNPJ4
         AND f.FORNECEDOR2 = d.CNPJ2
        WHERE 1=1
          {filtra_depositos} -- filtra_depositos
        ORDER BY
          d.CODIGO_DEPOSITO
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
