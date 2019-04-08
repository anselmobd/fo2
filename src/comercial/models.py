from pprint import pprint
from datetime import datetime, timedelta

from fo2.models import cursorF1, rows_to_dict_list, \
    rows_to_dict_list_lower

from utils.functions import dec_months


def busca_clientes(cnpj):
    cursor = cursorF1()
    sql = """
        SELECT FIRST 10000
          c.C_CGC CNPJ
        , c.C_RSOC CLIENTE
        FROM DIS_CLI c
        WHERE c.C_CGC STARTING WITH ?
           OR c.C_RSOC CONTAINING ?
        ORDER BY
          c.C_CGC
    """
    cursor.execute(sql, [cnpj[:14], cnpj])
    return rows_to_dict_list(cursor)


def ficha_cliente(cnpj):
    cursor = cursorF1()
    sql = """
        SELECT
          c.C_CGC CNPJ
        , c.C_RSOC CLIENTE
        , d.D_DUPNUM DUPLICATA
        , d.D_STAT STAT
        , d.D_PEDNUM PEDIDO
        , d.D_DFAT EMISSAO
        , d.D_DVENCORI VENC_ORI
        , d.D_DVENC VENCIMENTO
        , CASE WHEN mod(ord(d.D_AUX), 2) = 1
          THEN 'P'
          ELSE ' '
          END PRORROGADO
        , CASE WHEN d.D_VPAGO = 0 AND d.D_DVENC < 'NOW'
          THEN d.D_VALOR
          ELSE d.D_VALOR*(1-(d.D_DESC/100))
          END VALOR
        , d.D_QTD QUANT
        , d.D_QTDFAT QUANT_FAT
        , d.D_DPAGO DATA_PAGO
        , d.D_VPAGO VALOR_PAGO
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0 -- ''
            ELSE
              d.D_VPAGO - d.D_VALOR
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0 -- ''
            WHEN d.D_VPAGO <> 0 THEN
              d.D_VPAGO - d.D_VALOR
            ELSE
              d.D_VALOR
              * (d.D_JUROS * ((cast('NOW' AS DATE) - d.D_DVENC)
                              / 3000.0000))
            END
          END JUROS
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0
            ELSE
              d.D_DPAGO - d.D_DVENC
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0
            ELSE
              cast('NOW' AS DATE) - d.D_DVENC
            END
          END ATRASO
        , d.D_OP OP
        , d.D_BANCO BANCO
        , d.D_DESCONTO DESCONTO
        , d.D_OBS OBSERVACAO
        FROM DIS_DUP d
        LEFT JOIN DIS_CLI c
          ON c.C_CGC = d.D_CGC
        WHERE d.D_CGC = ?
          AND D.D_STAT >= '0' -- nao canceladas
          AND d.D_CODFIS IN ( '5101', '6101', '6107', '6109'
                            , '5124', '6124', '5125', '6125') -- cpof de venda
        ORDER BY
          d.D_DUPNUM
    """
    cursor.execute(sql, [cnpj])
    return rows_to_dict_list(cursor)


def get_vendas_cor(cursor, ref, periodo=None):
    hoje = datetime.now().date()
    ini_mes = hoje - timedelta(days=hoje.day-1)

    filtra_periodo = ''
    if periodo is not None:
        if periodo == '3m+':
            ini_periodo = dec_months(ini_mes, 3)
        elif periodo == '6m+':
            ini_periodo = dec_months(ini_mes, 6)
        elif periodo == '12m+':
            ini_periodo = dec_months(ini_mes, 12)
        elif periodo == '24m+':
            ini_periodo = dec_months(ini_mes, 24)
        filtra_periodo = "  AND v.dt >= TO_DATE('{}', 'yyyy-mm-dd')".format(
            ini_periodo.strftime('%Y-%m-%d'))

    sql = """
        WITH vendido AS
        (
        SELECT
          nf.NUM_NOTA_FISCAL NF
        , nf.DATA_EMISSAO DT
        , nf.NATOP_NF_NAT_OPER NATOP
        , nop.COD_NATUREZA COD_NAT
        , nop.DIVISAO_NATUR DIV_NAT
        , inf.NIVEL_ESTRUTURA NIVEL
        , inf.GRUPO_ESTRUTURA REF
        , TRIM(LEADING '0' FROM
               (REGEXP_REPLACE(inf.GRUPO_ESTRUTURA,
                               '^([^a-zA-Z]+)[a-zA-Z]*$', '\1'
                               ))) MODELO
        , inf.SUBGRU_ESTRUTURA TAM
        , inf.ITEM_ESTRUTURA COR
        , inf.QTDE_ITEM_FATUR QTD
        , inf.VALOR_UNITARIO PRECO
        , r.COLECAO COL
        , col.DESCR_COLECAO COLECAO
        FROM FATU_050 nf -- nota fiscal da Tussor - capa
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        JOIN PEDI_080 nop -- natureza da operação
          ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
         AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
        JOIN fatu_060 inf -- item de nf de saída
          ON inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
        LEFT JOIN BASI_030 r -- item (ref+tam+cor)
          on r.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
         AND r.REFERENCIA = inf.GRUPO_ESTRUTURA
        LEFT JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        --JOIN BASI_010 rtc -- item (ref+tam+cor)
        --  on rtc.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
        -- AND rtc.GRUPO_ESTRUTURA = inf.GRUPO_ESTRUTURA
        -- AND rtc.SUBGRU_ESTRUTURA = inf.SUBGRU_ESTRUTURA
        -- AND rtc.ITEM_ESTRUTURA = inf.ITEM_ESTRUTURA
        WHERE 1=1
          AND (nf.NATOP_NF_NAT_OPER IN (1, 2)
               OR (nop.DIVISAO_NATUR = 8
                   AND nop.COD_NATUREZA in ('5.11', '6.11')
                  )
              )
          AND nf.SITUACAO_NFISC = 1
          AND fe.DOCUMENTO IS NULL
        ORDER BY
        --  nf.NATOP_NF_NAT_OPER DESC
        --,
          nf.NUM_NOTA_FISCAL DESC
        , inf.SEQ_ITEM_NFISC
        )
        SELECT
          sum(v.qtd) qtd
        --, v.COLECAO
        --, v.MODELO
    """
    if ref != '':
        sql += """
            , v.REF
        """
    sql += """
        , v.COR
        FROM vendido v
        WHERE 1=1
        --  AND v.dt > TO_DATE('2019-01-01', 'yyyy-mm-dd')
        {filtra_periodo} -- filtra_periodo
        --  AND v.COL = 1
        --  AND v.MODELO = '417'
    """
    if ref != '':
        sql += """
            AND v.REF = '{}'
        """.format(ref)
    sql += """
        GROUP BY
        --  v.COLECAO
        --, v.MODELO
    """
    if ref != '':
        sql += """
              v.REF
            , v.COR
        """
    else:
        sql += """
            v.COR
        """
    sql += """
        ORDER BY
          1 DESC
        --, v.COLECAO
        --, v.MODELO
    """
    if ref != '':
        sql += """
            , v.REF
        """
    sql += """
        , v.COR
    """
    sql = sql.format(
        filtra_periodo=filtra_periodo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
