from fo2.models import rows_to_dict_list_lower


def repair_sequencia_estagio(cursor, periodo, oc, exec):

    # get new and old value to SEQUENCIA_ESTAGIO and ROWIDs
    sql_seq = '''
        SELECT
          ( SELECT
              count(DISTINCT l.ESTAGIO_ANTERIOR)
            FROM PCPC_040 l -- lote
            WHERE l.ORDEM_PRODUCAO = le.ORDEM_PRODUCAO
              AND l.ORDEM_CONFECCAO = le.ORDEM_CONFECCAO
              AND l.SEQ_OPERACAO <= le.SEQ_OPERACAO
          ) SEQ_NEW
        , le.SEQUENCIA_ESTAGIO SEQ_OLD
        , le.CODIGO_ESTAGIO EST
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
    alt = ''
    sep = ''
    ests = ''
    sep_ests = ''
    for seq in seqs:
        ests += '{}{}'.format(sep_ests, seq['est'])
        sep_ests = ', '
        if seq['seq_new'] != seq['seq_old']:
            if exec:
                cursor.execute(sql_setseq, [seq['seq_new'], seq['rid']])
            alt += '{}{}-{}'.format(sep, seq['seq_old'], seq['seq_new'])
            sep = ', '
            corrigido = True

    return corrigido, alt, ests
