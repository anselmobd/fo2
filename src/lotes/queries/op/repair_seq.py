from utils.functions.models import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def repair_sequencia_estagio(cursor, periodo, oc, exec):

    # get new and old value to SEQUENCIA_ESTAGIO and ROWIDs
    sql_seq = '''
        SELECT
          er.SEQUENCIA_ESTAGIO SEQ_NEW
        , le.SEQUENCIA_ESTAGIO SEQ_OLD
        , le.CODIGO_ESTAGIO EST
        , le.ROWID RID
        FROM pcpc_040 le
        JOIN pcpc_020 op
          ON op.ORDEM_PRODUCAO = le.ORDEM_PRODUCAO 
        JOIN MQOP_050 er
          ON er.NIVEL_ESTRUTURA = le.PROCONF_NIVEL99 
        AND er.GRUPO_ESTRUTURA = le.PROCONF_GRUPO 
        AND er.NUMERO_ALTERNATI = op.ALTERNATIVA_PECA 
        AND er.NUMERO_ROTEIRO = op.ROTEIRO_PECA 
        AND er.SEQ_OPERACAO = le.SEQ_OPERACAO 
        WHERE le.PERIODO_PRODUCAO = %s
          AND le.ORDEM_CONFECCAO = %s
        ORDER BY
          le.SEQ_OPERACAO
        , le.ROWID
    '''
    debug_cursor_execute(cursor, sql_seq, [periodo, oc])
    seqs = dictlist_lower(cursor)

    sql_setseq = '''
        UPDATE pcpc_040 le
        SET
          le.SEQUENCIA_ESTAGIO = %s
        WHERE le.ROWID = %s
    '''
    corrigido = False
    alt_list = []
    ests_list = []
    for seq in seqs:
        ests_list.append(f"{seq['est']}")
        if seq['seq_new'] != seq['seq_old']:
            if exec:
                debug_cursor_execute(cursor, sql_setseq, [seq['seq_new'], seq['rid']])
            alt_list.append(f"{seq['seq_old']}-{seq['seq_new']}")
            corrigido = True

    ests = ', '.join(ests_list)
    alt = ', '.join(alt_list)

    return corrigido, alt, ests
