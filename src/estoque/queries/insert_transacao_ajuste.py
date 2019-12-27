

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
