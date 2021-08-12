from pprint import pprint

from utils.functions.models import rows_to_dict_list


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


def unidades(cursor):
    sql = '''
        SELECT
          di.DIVISAO_PRODUCAO DIV
        , di.DESCRICAO DESCR
        , ci.ESTADO UF
        , ci.CIDADE
        , ' (' || lpad(fo.FORNECEDOR9, 8, '0')
          || '/' || lpad(fo.FORNECEDOR4, 4, '0')
          || '-' || lpad(fo.FORNECEDOR2, 2, '0')
          || ') '
          || fo.NOME_FORNECEDOR NOME
        FROM BASI_180 di -- divisão / unidade
        JOIN SUPR_010 fo -- fornacedor
          ON fo.FORNECEDOR9 = di.FACCIONISTA9
         AND fo.FORNECEDOR4 = di.FACCIONISTA4
         AND fo.FORNECEDOR2 = di.FACCIONISTA2
        JOIN BASI_160 ci -- cidade
          ON ci.COD_CIDADE = fo.COD_CIDADE
        WHERE di.DIVISAO_PRODUCAO > 1
          AND di.DIVISAO_PRODUCAO < 1000
        ORDER BY
          di.DIVISAO_PRODUCAO
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def estagios(cursor):
    sql = '''
        SELECT
          e.CODIGO_ESTAGIO EST
        , e.DESCRICAO DESCR
        , CASE WHEN e.CODIGO_DEPOSITO = 0 THEN ' '
          ELSE e.CODIGO_DEPOSITO || '-' || d.DESCRICAO
          END DEP
        , e.LEED_TIME LT
        FROM MQOP_005 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.CODIGO_DEPOSITO
        ORDER BY
          e.CODIGO_ESTAGIO
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def periodos_confeccao(cursor):
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO INI
        , p.DATA_FIM_PERIODO FIM
        FROM PCPC_010 p
        WHERE p.AREA_PERIODO = 1 -- confecção
        ORDER BY
          p.PERIODO_PRODUCAO
    '''
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
