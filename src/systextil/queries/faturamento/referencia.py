from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower


def referencias_vendidas(cursor):
    sql = f'''
        SELECT DISTINCT 
          inf.GRUPO_ESTRUTURA ref
        FROM FATU_050 nf -- nota fiscal da Tussor - capa
        JOIN PEDI_080 nop -- natureza da operação
          ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
         AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        JOIN FATU_060 inf -- nota fiscal da Tussor - capa
          ON inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
        WHERE 1=1
          AND nop.COD_NATUREZA in ('5.90', '6.90')
          AND nop.DIVISAO_NATUR = 1
          AND fe.DOCUMENTO IS NULL
          AND inf.NIVEL_ESTRUTURA = 1
    '''
    cursor.execute(sql)
    return dictlist_lower(cursor)
