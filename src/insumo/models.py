from django.db import models
from django.db import connections

import produto.models


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def item_count_nivel(cursor, ref, nivel=None):
    # verifica existêcia, unicidade e nível
    param = [ref, ]
    sql = """
        SELECT
          count(*) COUNT
        , min(r.NIVEL_ESTRUTURA) NIVEL
        FROM basi_030 r
        WHERE r.REFERENCIA = %s
    """
    if nivel is not None:
        sql = sql + """
            AND r.NIVEL_ESTRUTURA = %s
        """
        param.append(nivel)
    cursor.execute(sql, param)
    return rows_to_dict_list(cursor)


def ref_inform(cursor, nivel, ref):
    # Informações básicas
    sql = """
        SELECT
          r.DESCR_REFERENCIA DESCR
        , r.UNIDADE_MEDIDA || ' - ' || um.DESCR_UNIDADE UM
        , r.CONTA_ESTOQUE || ' - ' || ce.DESCR_CT_ESTOQUE CONTA_ESTOQUE
        , r.CLASSIFIC_FISCAL || ' - ' || cf.DESCR_CLASS_FISC NCM
        , r.CODIGO_CONTABIL || ' - ' || cc.DESCRICAO CODIGO_CONTABIL
        FROM basi_030 r
        JOIN basi_200 um
          ON um.unidade_medida = r.UNIDADE_MEDIDA
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        JOIN BASI_240 cf
          ON cf.CLASSIFIC_FISCAL = r.CLASSIFIC_FISCAL
        JOIN CONT_540 cc
          ON cc.TIPO_CONTABIL = 3
         AND cc.CODIGO_CONTABIL = r.CODIGO_CONTABIL
        WHERE r.NIVEL_ESTRUTURA = %s
         AND r.REFERENCIA = %s
    """
    cursor.execute(sql, [nivel, ref])
    return rows_to_dict_list(cursor)


def ref_cores(cursor, nivel, ref):
    return produto.models.prod_cores(cursor, nivel, ref)


def ref_tamanhos(cursor, nivel, ref):
    return produto.models.prod_tamanhos(cursor, nivel, ref)


def ref_parametros(cursor, nivel, ref):
    # Informações básicas
    sql = """
        SELECT
          p.SUBGRU_ESTRUTURA TAM
        , p.ITEM_ESTRUTURA COR
        , p.CODIGO_DEPOSITO || ' - ' || d.DESCRICAO DEPOSITO
        , p.ESTOQUE_MINIMO
        , p.ESTOQUE_MAXIMO
        , p.TEMPO_REPOSICAO LEAD
        FROM BASI_015 p
        JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = p.CODIGO_DEPOSITO
        WHERE p.NIVEL_ESTRUTURA = %s
          AND p.GRUPO_ESTRUTURA = %s
    """
    cursor.execute(sql, [nivel, ref])
    return rows_to_dict_list(cursor)
