import datetime
from functools import reduce
from operator import itemgetter, mul
from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.classes import Perf
from utils.functions import (
    fo2logger,
    my_make_key_cache,
)
from utils.functions.models.dictlist import dictlist

import produto.queries


def mapa_compras_necess_gerais_multi(cursor, dtini=None, nsem=None):
    p = Perf(id='mcngm', on=False)
    p.prt('mapa_compras_necess_gerais_multi')

    # key_cache = make_key_cache(ignore=['cursor'])
    key_cache = my_make_key_cache(
        'mapa_compras_necess_gerais_multi', dtini, nsem,
    )

    cached_result = cache.get(key_cache)

    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        p.prt('cached')
        return cached_result
    p.prt('calculating')

    nivel1 = mapa_compras_necessidades_gerais(cursor, dtini, nsem)

    debug = 9  # 1
    niveln = []
    for insumo in nivel1:
        if insumo['TEMALT']:

            if debug == 1:
                item = '.'.join([
                    insumo['CNIV'], insumo['CREF'],
                    insumo['CTAM_B'], insumo['CCOR_B']])
                pprint(item)
                if item == '2.TP010.TIN.0000MA':
                    pprint(insumo)
                    debug = 2

            subdata = produto.queries.CustoItem(
                cursor, insumo['CNIV'], insumo['CREF'],
                insumo['CTAM_B'], insumo['CCOR_B'],
                insumo['CALT']).get_data()

            consumo = {}
            for row in subdata:
                estrut_nivel = int(row['ESTRUT_NIVEL'])
                consumo[estrut_nivel] = row['CONSUMO'] 
                # o mapa_compras_necessidades_gerais já traz consumo
                # considerando banho
                # * (
                #     row['RBANHO'] if row['TCALC'] == 2 else 1)

                if debug == 2:
                    componente = '.'.join([
                        row['NIVEL'], row['REF'],
                        row['TAM'], row['COR']])
                    pprint(componente)
                    if componente == '9.CO003.UNI.000003':
                        pprint(row)
                        pprint(consumo)
                        debug = 3

                if estrut_nivel > 0:
                    consumo_final = reduce(
                        mul, list(consumo.values())[:estrut_nivel+1], 1)

                    if debug == 3:
                        print('consumo_final', consumo_final)
                        print('CCONSUMO_B',
                              insumo['CCONSUMO_B'] * consumo_final)
                        debug = 4

                    novoinsumo = {
                        'SEM': insumo['SEM'],
                        'OP': insumo['OP'],
                        'ALT': insumo['ALT'],
                        'NIV': insumo['NIV'],
                        'REF': insumo['REF'],
                        'LTAM': insumo['LTAM'],
                        'LCOR': insumo['LCOR'],
                        'EST': insumo['EST'],
                        'OS': insumo['OS'],
                        'QTD': insumo['QTD'],
                        'ATAM': insumo['ATAM'],
                        'ACOR': insumo['ACOR'],
                        'RBANHO': insumo['RBANHO'],
                        'CSEQ': row['SEQ'],
                        'CNIV': row['NIVEL'],
                        'CREF': row['REF'],
                        'CTAM': row['TAM'],
                        'CCOR': row['COR'],
                        'CALT': row['ALT'],
                        'CCONSUMO': insumo['CCONSUMO_B'] * consumo_final,
                        'TCALC': row['TCALC'],
                        'CCOR_B': row['COR'],
                        'CTAM_B': row['TAM'],
                        'CCONSUMO_B': insumo['CCONSUMO_B'] * consumo_final,
                        'TEMALT': row['TEMALT'],
                    }
                    niveln.append(novoinsumo)

    result = nivel1 + niveln
    cache.set(key_cache, result, timeout=entkeys._MINUTE * 2)
    fo2logger.info('calculated '+key_cache)
    p.prt('calculated')
    return result


def mapa_compras_necessidades_gerais(cursor, dtini=None, nsem=None):
    p = Perf(id='mcng', on=False)
    p.prt('mapa_compras_necessidades_gerais')

    # key_cache = make_key_cache(ignore=['cursor'])
    key_cache = my_make_key_cache(
        'mapa_compras_necessidades_gerais', dtini, nsem,
    )

    cached_result = cache.get(key_cache)

    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        p.prt('cached')
        return cached_result
    p.prt('calculating')

    passa_filtro_DATA_ENTRADA_CORTE = ''
    usa_filtro_DATA_ENTRADA_CORTE = ''
    if dtini is not None:
        passa_filtro_DATA_ENTRADA_CORTE = f""" --
            , '{dtini}' DATA
            , {nsem} SEMANAS
        """
        usa_filtro_DATA_ENTRADA_CORTE = """ --
            JOIN filtro f
              ON coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) <=
                 (TO_DATE(f.DATA,'YYYYMMDD')+6+7*f.SEMANAS+7)
        """

    sql = f"""
        WITH filtro AS
        (
        SELECT
          1 IGNORAR
        {passa_filtro_DATA_ENTRADA_CORTE} -- passa_filtro_DATA_ENTRADA_CORTE
        FROM DUAL
        )
        , oprod AS
        (
        SELECT
          TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw') SEM
        , op.ORDEM_PRODUCAO OP
        , op.REFERENCIA_PECA REF
        , op.ALTERNATIVA_PECA ALT
        FROM PCPC_020 op -- OP
        {usa_filtro_DATA_ENTRADA_CORTE} -- usa_filtro_DATA_ENTRADA_CORTE
        WHERE op.SITUACAO IN (2, 4) -- não cancelada
        )
        , oproditem AS
        (
        SELECT
          o.SEM
        , o.OP
        , o.ALT
        , l.PROCONF_NIVEL99 NIV
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO LTAM
        , l.PROCONF_ITEM LCOR
        , l.CODIGO_ESTAGIO EST
        , l.NUMERO_ORDEM OS
        , SUM(l.QTDE_A_PRODUZIR_PACOTE) QTD
        FROM PCPC_040 l -- lote
        JOIN oprod o
          ON o.OP = l.ORDEM_PRODUCAO
        WHERE l.QTDE_A_PRODUZIR_PACOTE <> 0
        GROUP BY
          o.SEM
        , o.OP
        , o.ALT
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        , l.CODIGO_ESTAGIO
        , l.NUMERO_ORDEM
        )
        , alternativa AS
        (
        SELECT DISTINCT
          i.*
        , e.SUB_ITEM ATAM
        , e.ITEM_ITEM ACOR
        , e.RELACAO_BANHO RBANHO
        FROM BASI_050 e
        JOIN oproditem i
          ON i.NIV = e.NIVEL_ITEM
         AND i.REF = e.GRUPO_ITEM
         AND i.ALT = e.ALTERNATIVA_ITEM
         AND ( e.SUB_ITEM = '000'
             OR i.LTAM = e.SUB_ITEM
             )
         AND ( e.ITEM_ITEM = '000000'
             OR i.LCOR = e.ITEM_ITEM
             )
        )
        , componentes AS
        (
        SELECT
          a.*
        , e.SEQUENCIA CSEQ
        , e.NIVEL_COMP CNIV
        , e.GRUPO_COMP CREF
        , e.SUB_COMP CTAM
        , e.ITEM_COMP CCOR
        , e.ALTERNATIVA_COMP CALT
        , e.CONSUMO CCONSUMO
        , e.TIPO_CALCULO TCALC
        FROM BASI_050 e
        JOIN alternativa a
          ON a.NIV = e.NIVEL_ITEM
         AND a.REF = e.GRUPO_ITEM
         AND a.ATAM = e.SUB_ITEM
         AND a.ACOR = e.ITEM_ITEM
         AND a.ALT = e.ALTERNATIVA_ITEM
         AND a.EST = e.ESTAGIO
        WHERE e.NIVEL_COMP <> 1
        )
        , comb_cor AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCOR = '000000'
          THEN b.ITEM_COMP
          ELSE c.CCOR
          END CCOR_B
        FROM BASI_040 b
        RIGHT JOIN componentes c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCOR = '000000'
             AND c.ATAM = b.SUB_ITEM
             AND c.LCOR = b.ITEM_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_tam AS
        (
        SELECT
          c.*
        , CASE WHEN c.CTAM = '000'
          THEN b.SUB_COMP
          ELSE c.CTAM
          END CTAM_B
        FROM BASI_040 b
        RIGHT JOIN comb_cor c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CTAM = '000'
             AND c.ACOR = b.ITEM_ITEM
             AND c.LTAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_consumo AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCONSUMO = 0
          THEN b.CONSUMO
          ELSE c.CCONSUMO
          END CCONSUMO_B
        FROM BASI_040 b
        RIGHT JOIN comb_tam c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCONSUMO = 0
             AND c.ACOR = b.ITEM_ITEM
             AND c.LTAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_com_alt AS
        (
        SELECT DISTINCT
          c.*
        , CASE WHEN e.NIVEL_ITEM IS NULL THEN 0 ELSE 1 END TEMALT
        FROM BASI_050 e
        RIGHT JOIN comb_consumo c
          ON c.CNIV = e.NIVEL_ITEM
         AND c.CREF = e.GRUPO_ITEM
         AND ( e.SUB_ITEM = '000'
             OR e.SUB_ITEM = c.CTAM
             )
         AND ( e.ITEM_ITEM = '000000'
             OR e.ITEM_ITEM = c.CCOR
             )
        )
        SELECT
          a.*
        FROM comb_com_alt a
    """

    cursor.execute(sql)

    cached_result = dictlist(cursor)
    cache.set(key_cache, cached_result, timeout=entkeys._MINUTE * 3)
    fo2logger.info('calculated '+key_cache)
    p.prt('calculated')
    return cached_result


def mapa_compras_necessidades_nivel_atual(cursor, nivel):
    '''
        Busca por referencia de nível o total de nessecidades (pedidos)
        até a semana atual.
    '''

    p = Perf(id='mcnna', on=False)
    p.prt('mapa_compras_necessidades_nivel_atual')

    dados_gerais = mapa_compras_necess_gerais_multi(cursor)

    result_dict = {}
    hoje = datetime.date.today()
    for row in dados_gerais:
        if row['CNIV'] == str(nivel) and row['SEM'].date() <= hoje:
            key = (row['CREF'], row['CTAM_B'], row['CCOR_B'])
            qtd = row['CCONSUMO_B'] * row['QTD']
            try:
                result_dict[key] += qtd
            except Exception:
                result_dict[key] = qtd

    p.prt('fim')
    return result_dict


def mapa_compras_necessidades_especificas(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None, colunas='m'):
    '''
    colunas
        m: Como no mapa de compras
        t: Todas as colunas
    '''

    p = Perf(id='mcne', on=False)
    p.prt('mapa_compras_necessidades_especificas')

    dados_gerais = mapa_compras_necess_gerais_multi(cursor, dtini, nsem)

    dados = [
        dado for dado in dados_gerais
        if dado['CNIV'] == str(nivel)
        and dado['CREF'] == ref
        and dado['CTAM_B'] == tam
        and dado['CCOR_B'] == cor
    ]

    if colunas == 't':
        p.prt('ordenar')
        dados = sorted(dados, key=itemgetter(
            'SEM',
            'OP',
            'ALT',
            'NIV',
            'REF',
            'LTAM',
            'LCOR',
            'EST',
        ))
        p.prt('fim')
        return dados

    # if colunas == 'm'
    p.prt('montar result')
    result_dict = {}
    for row in dados:
        sem = row['SEM']
        qtd = row['CCONSUMO_B'] * row['QTD']
        try:
            result_dict[sem] += qtd
        except Exception:
            result_dict[sem] = qtd
    result = [{'SEMANA_NECESSIDADE': sem,
               'QTD_INSUMO': result_dict[sem]}
              for sem in sorted(result_dict.keys())]

    p.prt('fim')
    return result


def mapa_compras_necessidades(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None, colunas='m'):

    # key_cache = make_key_cache(ignore=['cursor'])
    key_cache = my_make_key_cache(
        'mapa_compras_necessidades', nivel, ref, cor, tam, dtini, nsem,
        colunas)

    cached_result = cache.get(key_cache)

    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    passa_filtro_DATA_ENTRADA_CORTE = ''
    usa_filtro_DATA_ENTRADA_CORTE = ''
    if dtini is not None:
        passa_filtro_DATA_ENTRADA_CORTE = f""" --
            , '{dtini}' DATA
            , {nsem} SEMANAS
        """
        usa_filtro_DATA_ENTRADA_CORTE = """ --
            JOIN filtro f
              ON coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) <=
                 (TO_DATE(f.DATA,'YYYYMMDD')+6+7*f.SEMANAS+7)
        """

    sql = f"""
        WITH filtro AS
        (
        SELECT
          '{nivel}' NIV
        , '{ref}' REF
        , '{tam}' TAM
        , '{cor}' COR
        {passa_filtro_DATA_ENTRADA_CORTE} -- passa_filtro_DATA_ENTRADA_CORTE
        FROM DUAL
        )
        , oprod AS
        (
        SELECT
          TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw') SEM
        , op.ORDEM_PRODUCAO OP
        , op.REFERENCIA_PECA REF
        , op.ALTERNATIVA_PECA ALT
        FROM PCPC_020 op -- OP
        {usa_filtro_DATA_ENTRADA_CORTE} -- usa_filtro_DATA_ENTRADA_CORTE
        WHERE op.SITUACAO IN (2, 4) -- não cancelada
        )
        , oproditem AS
        (
        SELECT
          o.SEM
        , o.OP
        , o.ALT
        , l.PROCONF_NIVEL99 NIV
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO LTAM
        , l.PROCONF_ITEM LCOR
        , l.CODIGO_ESTAGIO EST
        , l.NUMERO_ORDEM OS
        , SUM(l.QTDE_A_PRODUZIR_PACOTE) QTD
        FROM PCPC_040 l -- lote
        JOIN oprod o
          ON o.OP = l.ORDEM_PRODUCAO
        WHERE l.QTDE_A_PRODUZIR_PACOTE <> 0
        GROUP BY
          o.SEM
        , o.OP
        , o.ALT
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        , l.CODIGO_ESTAGIO
        , l.NUMERO_ORDEM
        )
        , alternativa AS
        (
        SELECT DISTINCT
          i.*
        , e.SUB_ITEM ATAM
        , e.ITEM_ITEM ACOR
        , e.RELACAO_BANHO RBANHO
        FROM BASI_050 e
        JOIN oproditem i
          ON i.NIV = e.NIVEL_ITEM
         AND i.REF = e.GRUPO_ITEM
         AND i.ALT = e.ALTERNATIVA_ITEM
         AND ( e.SUB_ITEM = '000'
             OR i.LTAM = e.SUB_ITEM
             )
         AND ( e.ITEM_ITEM = '000000'
             OR i.LCOR = e.ITEM_ITEM
             )
        )
        , componentes AS
        (
        SELECT
          a.*
        , e.SEQUENCIA CSEQ
        , e.NIVEL_COMP CNIV
        , e.GRUPO_COMP CREF
        , e.SUB_COMP CTAM
        , e.ITEM_COMP CCOR
        , e.ALTERNATIVA_COMP CALT
        , e.CONSUMO CCONSUMO
        , e.TIPO_CALCULO TCALC
        FROM BASI_050 e
        JOIN alternativa a
          ON a.NIV = e.NIVEL_ITEM
         AND a.REF = e.GRUPO_ITEM
         AND a.ATAM = e.SUB_ITEM
         AND a.ACOR = e.ITEM_ITEM
         AND a.ALT = e.ALTERNATIVA_ITEM
         AND a.EST = e.ESTAGIO
        WHERE e.NIVEL_COMP <> 1
        )
        , comb_cor AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCOR = '000000'
          THEN b.ITEM_COMP
          ELSE c.CCOR
          END CCOR_B
        FROM BASI_040 b
        RIGHT JOIN componentes c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCOR = '000000'
             AND c.ATAM = b.SUB_ITEM
             AND c.LCOR = b.ITEM_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_tam AS
        (
        SELECT
          c.*
        , CASE WHEN c.CTAM = '000'
          THEN b.SUB_COMP
          ELSE c.CTAM
          END CTAM_B
        FROM BASI_040 b
        RIGHT JOIN comb_cor c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CTAM = '000'
             AND c.ACOR = b.ITEM_ITEM
             AND c.LTAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_consumo AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCONSUMO = 0
          THEN b.CONSUMO
          ELSE c.CCONSUMO
          END CCONSUMO_B
        FROM BASI_040 b
        RIGHT JOIN comb_tam c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCONSUMO = 0
             AND c.ACOR = b.ITEM_ITEM
             AND c.LTAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_com_alt AS
        (
        SELECT DISTINCT
          c.*
        , CASE WHEN e.NIVEL_ITEM IS NULL THEN 0 ELSE 1 END TEMALT
        FROM BASI_050 e
        RIGHT JOIN comb_consumo c
          ON c.CNIV = e.NIVEL_ITEM
         AND c.CREF = e.GRUPO_ITEM
         AND ( e.SUB_ITEM = '000'
             OR e.SUB_ITEM = c.CTAM
             )
         AND ( e.ITEM_ITEM = '000000'
             OR e.ITEM_ITEM = c.CCOR
             )
        )
        , filtrado AS
        (
        SELECT
          a.*
        FROM comb_com_alt a
        JOIN filtro f
          ON f.NIV = a.CNIV
         AND f.REF = a.CREF
         AND f.TAM = a.CTAM_B
         AND f.COR = a.CCOR_B
        ORDER BY
          a.SEM
        , a.OP
        , a.ALT
        , a.NIV
        , a.REF
        , a.LTAM
        , a.LCOR
        , a.EST
        , a.OS
        , a.CSEQ
        )
    """
    if colunas == 'm':
        sql += f"""
            SELECT
              a.SEM SEMANA_NECESSIDADE
            , sum(a.CCONSUMO_B * a.QTD) QTD_INSUMO
            FROM filtrado a
            GROUP BY
              a.SEM
            ORDER BY
              a.SEM
        """
    elif colunas == 't':
        sql += f"""
            SELECT
              a.*
            FROM filtrado a
        """

    cursor.execute(sql)

    cached_result = dictlist(cursor)
    cache.set(key_cache, cached_result, timeout=entkeys._MINUTE)
    fo2logger.info('calculated '+key_cache)
    return cached_result
