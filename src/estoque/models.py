import time
import datetime
from pprint import pprint

from django.db import models

from fo2.models import rows_to_dict_list_lower


def estoque_deposito_ref(cursor, deposito, ref, modelo=None):
    filtro_ref = ''
    if ref is not None and ref != '-':
        filtro_ref = '''--
            AND rtc.GRUPO_ESTRUTURA = '{ref}'
        '''.format(
            ref=ref,
        )

    filtro_modelo = ''
    if modelo is not None and modelo != '-':
        if '-' in modelo:
            modelos = modelo.split('-')
            filtro_modelo = '''--
                AND
                  TO_NUMBER(
                    TRIM(
                      LEADING '0' FROM (
                        REGEXP_REPLACE(
                          rtc.GRUPO_ESTRUTURA,
                          '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                          '\\1'
                        )
                      )
                    )
                  ) >= TO_NUMBER('{modelo_ini}')
                AND
                  TO_NUMBER(
                    TRIM(
                      LEADING '0' FROM (
                        REGEXP_REPLACE(
                          rtc.GRUPO_ESTRUTURA,
                          '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                          '\\1'
                        )
                      )
                    )
                  ) <= TO_NUMBER('{modelo_fim}')
            '''.format(
                modelo_ini=modelos[0],
                modelo_fim=modelos[1],
            )
        else:
            filtro_modelo = '''--
                AND
                  TRIM(
                    LEADING '0' FROM (
                      REGEXP_REPLACE(
                        rtc.GRUPO_ESTRUTURA,
                        '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                        '\\1'
                      )
                    )
                  ) = '{modelo}'
            '''.format(
                modelo=modelo,
            )

    sql = '''
        SELECT
          i.MODELO
        , i.REF
        , i.COR
        , ta.ORDEM_TAMANHO
        , i.TAM
        , i.DEP
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QTD
        FROM (
          SELECT
            TO_NUMBER(
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    rtc.GRUPO_ESTRUTURA,
                    '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              )
            ) MODELO
          , rtc.GRUPO_ESTRUTURA REF
          , rtc.SUBGRU_ESTRUTURA TAM
          , rtc.ITEM_ESTRUTURA COR
          , d.CODIGO_DEPOSITO DEP
          FROM BASI_010 rtc, BASI_205 d
          WHERE 1=1
            AND rtc.NIVEL_ESTRUTURA = 1
            AND d.CODIGO_DEPOSITO = '{deposito}'
            AND rtc.GRUPO_ESTRUTURA < 'C0000'
            AND REGEXP_LIKE (
                  rtc.GRUPO_ESTRUTURA
                , '^0?[abAB]?([0-9]+)[a-zA-Z]*$'
                )
            {filtro_ref} -- filtro_ref
            {filtro_modelo} -- filtro_modelo
        ) i
        LEFT JOIN BASI_220 ta
          ON ta.TAMANHO_REF = i.TAM
        LEFT JOIN ESTQ_040 e
          ON e.LOTE_ACOMP = 0
         AND e.CDITEM_NIVEL99 = 1
         AND e.CDITEM_GRUPO = i.REF
         AND e.CDITEM_SUBGRUPO = i.TAM
         AND e.CDITEM_ITEM = i.COR
         AND e.DEPOSITO = i.DEP
        ORDER BY
          i.MODELO
        , NLSSORT(i.REF,'NLS_SORT=BINARY_AI')
        , i.COR
        , ta.ORDEM_TAMANHO
    '''.format(
        deposito=deposito,
        filtro_ref=filtro_ref,
        filtro_modelo=filtro_modelo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def trans_fo2_deposito_ref(
        cursor, deposito, ref, cor=None, tam=None,
        tipo='f', data=None, hora=None):

    filtro_cor = ''
    if cor is not None:
        filtro_cor = '''--
            AND t.ITEM_ESTRUTURA = '{}'
        '''.format(cor)

    filtro_tam = ''
    if tam is not None:
        filtro_tam = '''--
            AND t.SUBGRUPO_ESTRUTURA = '{}'
        '''.format(tam)

    filtro_tipo = ''
    if tipo == 'f':  # fo2
        filtro_tipo = '''--
            AND t.NUMERO_DOCUMENTO >= 702000000
            AND t.NUMERO_DOCUMENTO <= 702999999
        '''
    elif tipo == 's':  # systextil
        filtro_tipo = '''--
            AND (  t.NUMERO_DOCUMENTO < 702000000
                OR t.NUMERO_DOCUMENTO > 702999999
                )
        '''

    filtro_data = ''
    if data is not None:
        if hora is None:
            data_hora = data
        else:
            data_hora = datetime.datetime.combine(data, hora)
        filtro_data = '''--
            AND t.DATA_INSERCAO >= TIMESTAMP '{}'
        '''.format(
            data_hora.strftime('%Y-%m-%d %H:%M:%S')
        )

    sql = '''
        SELECT
          t.DATA_INSERCAO HORA
        , t.NUMERO_DOCUMENTO NUMDOC
        , t.ITEM_ESTRUTURA COR
        , t.SUBGRUPO_ESTRUTURA TAM
        , t.CODIGO_TRANSACAO TRANS
        , t.ENTRADA_SAIDA ES
        , t.QUANTIDADE QTD
        FROM ESTQ_300 t
        WHERE t.CODIGO_DEPOSITO = '{deposito}'
          AND t.NIVEL_ESTRUTURA = '1'
          AND t.GRUPO_ESTRUTURA = '{ref}'
          {filtro_cor} -- filtro_cor
          {filtro_tam} -- filtro_tam
          {filtro_data} -- filtro_data
          {filtro_tipo} -- filtro_tipo
        ORDER BY
          t.DATA_INSERCAO DESC
    '''.format(
        deposito=deposito,
        ref=ref,
        filtro_cor=filtro_cor,
        filtro_tam=filtro_tam,
        filtro_data=filtro_data,
        filtro_tipo=filtro_tipo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_estoque_dep_ref_cor_tam(cursor, deposito, ref, cor, tam):
    sql = '''
        SELECT
          e.QTDE_ESTOQUE_ATU ESTOQUE
        FROM ESTQ_040 e
        WHERE 1=1
          AND e.CDITEM_NIVEL99 = 1
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.CDITEM_SUBGRUPO = '{tam}'
          AND e.CDITEM_ITEM = '{cor}'
          AND e.DEPOSITO = {deposito}
    '''.format(
        deposito=deposito,
        ref=ref,
        cor=cor,
        tam=tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_preco_medio_ref_cor_tam(cursor, ref, cor, tam):
    filtra_tam = ''
    if tam != '000':
        filtra_tam = """--
            AND rtc.SUBGRU_ESTRUTURA = '{tam}'
        """.format(tam=tam)

    sql = '''
        SELECT
          rtc.GRUPO_ESTRUTURA REF
        , rtc.SUBGRU_ESTRUTURA TAM
        , rtc.ITEM_ESTRUTURA COR
        , coalesce(rtc.PRECO_MEDIO, 0) PRECO_MEDIO
        FROM BASI_010 rtc
        WHERE 1=1
          AND rtc.NIVEL_ESTRUTURA = 1
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          {filtra_tam} -- filtra_tam
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    '''.format(
        ref=ref,
        cor=cor,
        filtra_tam=filtra_tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def insert_transacao_ajuste(
        cursor, deposito, ref, tam, cor, num_doc, trans, es, ajuste,
        preco_medio):
    sql = '''
        INSERT INTO ESTQ_300 (
          CODIGO_DEPOSITO
        , NIVEL_ESTRUTURA
        , GRUPO_ESTRUTURA
        , SUBGRUPO_ESTRUTURA
        , ITEM_ESTRUTURA
        , DATA_MOVIMENTO
        , SEQUENCIA_FICHA
        , SEQUENCIA_INSERCAO
        , NUMERO_LOTE
        , NUMERO_DOCUMENTO
        , SERIE_DOCUMENTO
        , CNPJ_9
        , CNPJ_4
        , CNPJ_2
        , SEQUENCIA_DOCUMENTO
        , CODIGO_TRANSACAO
        , ENTRADA_SAIDA
        , CENTRO_CUSTO
        , QUANTIDADE
        , SALDO_FISICO
        , VALOR_MOVIMENTO_UNITARIO
        , VALOR_CONTABIL_UNITARIO
        , PRECO_MEDIO_UNITARIO
        , SALDO_FINANCEIRO
        , GRUPO_MAQUINA
        , SUBGRU_MAQUINA
        , NUMERO_MAQUINA
        , ORDEM_SERVICO
        , CONTABILIZADO
        , USUARIO_SYSTEXTIL
        , PROCESSO_SYSTEXTIL
        , DATA_INSERCAO
        , USUARIO_REDE
        , MAQUINA_REDE
        , APLICATIVO
        , TABELA_ORIGEM
        , FLAG_ELIMINA
        , VALOR_MOVIMENTO_UNITARIO_PROJ
        , VALOR_CONTABIL_UNITARIO_PROJ
        , PRECO_MEDIO_UNITARIO_PROJ
        , SALDO_FINANCEIRO_PROJ
        , VALOR_MOVTO_UNIT_ESTIMADO
        , PRECO_MEDIO_UNIT_ESTIMADO
        , SALDO_FINANCEIRO_ESTIMADO
        , VALOR_TOTAL
        , PROJETO
        , SUBPROJETO
        , SERVICO
        , QUANTIDADE_QUILO
        , SALDO_FISICO_QUILO
        , ESTAGIO_OP
        , NUMERO_NF
        , NUMERO_OP
        , NUMERO_OS
        , TIPO_ORDEM
        , TIPO_SPED_TRANSACAO
        ) VALUES (
          {deposito}  -- CODIGO_DEPOSITO
        , '1'  -- NIVEL_ESTRUTURA
        , '{ref}'  -- GRUPO_ESTRUTURA
        , '{tam}'  -- SUBGRUPO_ESTRUTURA
        , '{cor}'  -- ITEM_ESTRUTURA
        , sysdate  -- TIMESTAMP '2019-11-28 00:00:00.000000'  -- DATA_MOVIMENTO
        , 0  -- SEQUENCIA_FICHA
        , 1  -- SEQUENCIA_INSERCAO
        , 0  -- NUMERO_LOTE
        , {num_doc}  -- NUMERO_DOCUMENTO
        , NULL  -- SERIE_DOCUMENTO
        , 0  -- CNPJ_9
        , 0  -- CNPJ_4
        , 0  -- CNPJ_2
        , 0  -- SEQUENCIA_DOCUMENTO
        , {trans}  -- CODIGO_TRANSACAO
        , '{es}'  -- ENTRADA_SAIDA
        , 0  -- CENTRO_CUSTO
        , {ajuste}  -- QUANTIDADE
        , 0  -- SALDO_FISICO
        , {preco_medio}  -- VALOR_MOVIMENTO_UNITARIO
        , 0  -- 2  -- VALOR_CONTABIL_UNITARIO
        , 0  -- PRECO_MEDIO_UNITARIO
        , 0  -- SALDO_FINANCEIRO
        , NULL  -- GRUPO_MAQUINA
        , NULL  -- SUBGRU_MAQUINA
        , 0  -- NUMERO_MAQUINA
        , NULL  -- ORDEM_SERVICO
        , 0  -- CONTABILIZADO
        , 'ANSELMO_SIS'  -- USUARIO_SYSTEXTIL
        , 'estq_f950'  -- PROCESSO_SYSTEXTIL
        , sysdate  -- TIMESTAMP '2019-11-28 12:00:00.000000'  -- DATA_INSERCAO
        , 'ANSELMO_SIS'  -- USUARIO_REDE
        , '192.168.1.242'  -- MAQUINA_REDE
        , 'estq_f950'  -- APLICATIVO
        , 'ESTQ_300'  -- TABELA_ORIGEM
        , 0  -- FLAG_ELIMINA
        , 0  -- VALOR_MOVIMENTO_UNITARIO_PROJ
        , 0  -- VALOR_CONTABIL_UNITARIO_PROJ
        , 0  -- PRECO_MEDIO_UNITARIO_PROJ
        , 0  -- SALDO_FINANCEIRO_PROJ
        , 0  -- VALOR_MOVTO_UNIT_ESTIMADO
        , 0  -- PRECO_MEDIO_UNIT_ESTIMADO
        , 0  -- SALDO_FINANCEIRO_ESTIMADO
        , {valor_total}  -- VALOR_TOTAL
        , 0  -- PROJETO
        , 0  -- SUBPROJETO
        , 0  -- SERVICO
        , 0  -- QUANTIDADE_QUILO
        , 0  -- SALDO_FISICO_QUILO
        , NULL  -- ESTAGIO_OP
        , NULL  -- NUMERO_NF
        , NULL  -- NUMERO_OP
        , NULL  -- NUMERO_OS
        , NULL  -- TIPO_ORDEM
        , NULL  -- TIPO_SPED_TRANSACAO
        )
    '''.format(
        deposito=deposito,
        ref=ref,
        tam=tam,
        cor=cor,
        num_doc=num_doc,
        trans=trans,
        es=es,
        ajuste=ajuste,
        preco_medio=preco_medio,
        valor_total=ajuste*preco_medio,
    )
    try:
        cursor.execute(sql)
        return True
    except Exception:
        return False
