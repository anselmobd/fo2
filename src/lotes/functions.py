
def repair_sequencia_estagio(cursor, periodo, oc):

    # get new and old value to SEQUENCIA_ESTAGIO and ROWIDs
    sql_seq = '''
        SELECT
          ROW_NUMBER() OVER (
            PARTITION BY le.ORDEM_CONFECCAO
            ORDER BY le.SEQ_OPERACAO, le.ROWID
          ) SEQ_NEW
        , le.SEQUENCIA_ESTAGIO SEQ_OLD
        , le.ROWID RID
        FROM pcpc_040 le
        WHERE le.PERIODO_PRODUCAO = %s
          AND le.ORDEM_CONFECCAO = %s
        ORDER BY
          le.SEQ_OPERACAO
        , le.ROWID
    '''
    cursor.execute(sql_seq, [periodo, oc])
    seqs = rows_to_dict_list_lower(cursor)

    sql_setseq = '''
        UPDATE pcpc_040 le
        SET
          le.SEQUENCIA_ESTAGIO = %s
        WHERE le.ROWID = %s
    '''
    corrigido = False
    for seq in seqs:
        if seq['seq_new'] != seq['seq_old']:
            cursor.execute(sql_setseq, [seq['seq'], seq['rid']])
            corrigido = True

    return corrigido
