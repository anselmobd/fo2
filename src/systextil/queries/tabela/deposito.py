from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def query_deposito(cursor, only=None, less=None, empresa=None):

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

    filtro_empresa = f"AND d.LOCAL_DEPOSITO = {empresa}" if empresa else ''

    sql = f'''
        SELECT
          d.CODIGO_DEPOSITO COD
        , d.LOCAL_DEPOSITO EMPRESA
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
          {filtro_empresa} -- filtro_empresa
        ORDER BY
          d.CODIGO_DEPOSITO
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
