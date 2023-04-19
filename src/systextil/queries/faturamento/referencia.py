from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def referencias_vendidas(cursor):
    sql = f'''
        SELECT DISTINCT 
          inf.GRUPO_ESTRUTURA ref
        , max(nf.DATA_EMISSAO) data_emissao
        FROM FATU_050 nf -- nota fiscal da Tussor - capa
        JOIN PEDI_080 nop -- natureza da operação
          ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
         AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        JOIN FATU_060 inf -- nota fiscal da Tussor - capa
          ON inf.ch_it_nf_cd_empr = nf.codigo_empresa
         and inf.ch_it_nf_num_nfis = nf.num_nota_fiscal
         and inf.ch_it_nf_ser_nfis = nf.serie_nota_fisc
         AND inf.NR_CAIXA = 0
        JOIN estq_005 t
          ON t.CODIGO_TRANSACAO = inf.TRANSACAO
        WHERE 1=1
          -- ou o faturamento tem uma transação de venda
          -- ou é o caso especial de remessa de residuo
          AND ( t.TIPO_TRANSACAO = 'V'
              OR nf.NATOP_NF_NAT_OPER = 900
              )
          -- filtro de faturamento baseado na view Faturados_X_Devolvidos
          -- filtrando faturamento_Sim_Nao = "Sim" e por data
          -- não cancelada
          AND nf.COD_CANC_NFISC = 0
          -- utilizou natureza configurada como faturamento
          AND nop.faturamento = 1
          --AND nop.COD_NATUREZA in ('5.90', '6.90')
          --AND nop.DIVISAO_NATUR = 1
          AND fe.DOCUMENTO IS NULL
          AND inf.NIVEL_ESTRUTURA = 1
        GROUP BY 
          inf.GRUPO_ESTRUTURA
        ORDER BY 
          inf.GRUPO_ESTRUTURA
    '''
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['modelo'] = modelo_de_ref(row['ref'])
    return data
