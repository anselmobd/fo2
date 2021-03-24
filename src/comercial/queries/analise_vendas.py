from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def analise_vendas(cursor, ref=None, por=None):
  
    sql_base = (
    f"""WITH item_vendido AS
        ( SELECT
            nf.DATA_EMISSAO DT
          , r.COLECAO COL
          , r.CGC_CLIENTE_9 CNPJ9
          , inf.NIVEL_ESTRUTURA NIVEL
          , inf.GRUPO_ESTRUTURA REF
          , inf.SUBGRU_ESTRUTURA TAM
          , inf.ITEM_ESTRUTURA COR
          , sum(inf.QTDE_ITEM_FATUR) QTD
          FROM FATU_050 nf -- nota fiscal da Tussor - capa
          LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
            ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
          AND fe.SITUACAO_ENTRADA = 1 -- ativa
          JOIN PEDI_080 nop -- natureza da operação
            ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
          AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
          JOIN fatu_060 inf -- item de nf de saída
            ON inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
          LEFT JOIN BASI_030 r -- ref
            on r.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
          AND r.REFERENCIA = inf.GRUPO_ESTRUTURA
          WHERE 1=1
            AND nf.SITUACAO_NFISC = 1
            AND fe.DOCUMENTO IS NULL
            AND (nf.NATOP_NF_NAT_OPER IN (1, 2)
                OR (nop.DIVISAO_NATUR = 8
                    AND nop.COD_NATUREZA in ('5.11', '6.11')
                    )
                )
          GROUP BY 
            nf.DATA_EMISSAO
          , r.COLECAO
          , r.CGC_CLIENTE_9
          , inf.NIVEL_ESTRUTURA
          , inf.GRUPO_ESTRUTURA
          , inf.SUBGRU_ESTRUTURA
          , inf.ITEM_ESTRUTURA
        )
    """)

    filtra_ref = ""
    if ref is not None:
        filtra_ref = f"AND iv.REF = '{ref}'"

    select_fields = (
    """ iv.DT
      , iv.COL
      , iv.CNPJ9
      , iv.NIVEL
      , iv."REF"
      , iv.TAM
      , iv.COR
      , iv.QTD
    """)
    sum_fields = ""
    group_fields = select_fields
    order_fields = select_fields

    if por == 'ref':
        select_fields = (
        """iv."REF"
        """)
        sum_fields = (
        """, sum(iv.QTD) QTD
        """)
        group_fields = select_fields
        order_fields = select_fields

    if por == 'qtd_ref':
        select_fields = (
        """iv."REF"
        """)
        sum_fields = (
        """, sum(iv.QTD) QTD
        """)
        group_fields = select_fields
        order_fields = '2 DESC'

    sql = f"""
        {sql_base} -- sql_base
        SELECT 
          {select_fields} -- select_fields
          {sum_fields} -- sum_fields
        FROM item_vendido iv
        WHERE 1=1
          {filtra_ref} -- filtra_ref
        GROUP BY
          {group_fields} -- group_fields
        ORDER BY
          {order_fields} -- order_fields
    """

    cursor.execute(sql)
    cached_result = rows_to_dict_list_lower(cursor)
    return cached_result
