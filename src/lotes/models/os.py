from utils.functions.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *
from lotes.queries.os import *


def os_inform(cursor, os):
    # Informações sobre OS
    return get_os(cursor, os=os)


def os_op(cursor, os):
    # Totais por OP
    sql = """
        SELECT
          l.ORDEM_PRODUCAO OP
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(
            CASE WHEN l.QTDE_A_PRODUZIR_PACOTE <> 0
            THEN l.QTDE_A_PRODUZIR_PACOTE
            ELSE --l.QTDE_PECAS_PROG
              QTDE_PECAS_PROD
            + QTDE_CONSERTO
            + QTDE_PECAS_2A
            + QTDE_PERDAS
            END
          ) QTD
        , o.PEDIDO_VENDA PEDIDO
        , COALESCE(ped.COD_PED_CLIENTE, '') PED_CLIENTE
        FROM pcpc_040 l -- lotes
        JOIN PCPC_020 o -- OP
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
        WHERE l.NUMERO_ORDEM = %s
        GROUP BY
          l.ORDEM_PRODUCAO
        , o.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)


def os_lotes(cursor, os):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, os=os)


def os_sortimento(cursor, os):
    # Grade de OS
    grade = GradeQtd(cursor, [os])

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql='''
            SELECT DISTINCT
              s.PRODORD_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO
            FROM OBRF_081 s
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = s.PRODORD_SUBGRUPO
            WHERE s.NUMERO_ORDEM = %s
            ORDER BY
              tam.ORDEM_TAMANHO
        '''
        )

    # cores
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Produto-Cor',
        name_plural='Produtos-Cores',
        sql='''
            SELECT
              s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM SORTIMENTO
            , s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM || ' - ' ||
              max( p.DESCRICAO_15 ) DESCR
            FROM OBRF_081 s
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = s.PRODORD_GRUPO
             AND p.ITEM_ESTRUTURA = s.PRODORD_ITEM
            WHERE s.NUMERO_ORDEM = %s
            GROUP BY
              s.PRODORD_GRUPO
            , s.PRODORD_ITEM
            ORDER BY
              2
        '''
        )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
            SELECT
              s.PRODORD_GRUPO || ' - ' || s.PRODORD_ITEM SORTIMENTO
            , s.PRODORD_SUBGRUPO TAMANHO
            , s.QTDE_ARECEBER QUANTIDADE
            FROM OBRF_081 s
            WHERE s.NUMERO_ORDEM = %s
        '''
        )

    return (grade.table_data['header'], grade.table_data['fields'],
            grade.table_data['data'])


def os_itens(cursor, os):
    # Itens para nota de OS
    sql = """
        SELECT
          s.PRODSAI_NIVEL99 NIVEL
        , s.PRODSAI_GRUPO REF
        , s.PRODSAI_ITEM COR
        , s.PRODSAI_SUBGRUPO TAM
        , i.NARRATIVA
        , r.UNIDADE_MEDIDA UN
        , s.VALOR_PRODUTO VALOR_UN
        , s.QTDE_ESTRUTURA QTD_ESTR
        , s.QTDE_ENVIADA QTD_ENV
        , s.NUM_NF_SAI NF
        , nf.DATA_EMISSAO DATA_NF
        , ce.DATA_EMISSAO - nf.DATA_EMISSAO DIAS
        , ie.CAPA_ENT_NRDOC NF_RETORNO
        , ce.DATA_EMISSAO DATA_RETORNO
        , ie.QUANTIDADE QTD_RETORNO
        , CASE
          WHEN ie.QUANTIDADE = s.QTDE_ENVIADA THEN 'Total'
          WHEN ie.QUANTIDADE < s.QTDE_ENVIADA THEN 'Parcial'
          ELSE 'Verificar'
          END RETORNO
        , CASE WHEN s.PRODSAI_NIVEL99 = 1 THEN
            CASE
            WHEN ce.NATOPER_NAT_OPER = 22 THEN 'Sim'
            WHEN ce.NATOPER_NAT_OPER = 23 THEN 'Não'
            ELSE 'Verificar'
            END
          ELSE '-'
          END APLICADO
        FROM OBRF_082 s
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = s.PRODSAI_NIVEL99
         AND i.GRUPO_ESTRUTURA = s.PRODSAI_GRUPO
         AND i.SUBGRU_ESTRUTURA = s.PRODSAI_SUBGRUPO
         AND i.ITEM_ESTRUTURA = s.PRODSAI_ITEM
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = s.PRODSAI_NIVEL99
         AND r.REFERENCIA = s.PRODSAI_GRUPO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = s.PRODSAI_SUBGRUPO
        LEFT JOIN FATU_050 nf -- nota fiscal da Tussor
          ON nf.NUM_NOTA_FISCAL = s.NUM_NF_SAI
        LEFT JOIN OBRF_015 ie -- item de nota fiscal de entrada
          ON s.NUM_NF_SAI <> 0
         AND ie.NUM_NOTA_ORIG = s.NUM_NF_SAI
         AND ie.CODITEM_NIVEL99 = s.PRODSAI_NIVEL99
         AND ie.CODITEM_GRUPO = s.PRODSAI_GRUPO
         AND ie.CODITEM_SUBGRUPO = s.PRODSAI_SUBGRUPO
         AND ie.CODITEM_ITEM = s.PRODSAI_ITEM
        LEFT JOIN OBRF_010 ce -- capa de nota fiscal de entrada
          ON ce.DOCUMENTO = ie.CAPA_ENT_NRDOC
         AND ce.CGC_CLI_FOR_9 = ie.CAPA_ENT_FORCLI9
         AND ce.CGC_CLI_FOR_4 = ie.CAPA_ENT_FORCLI4
        WHERE s.NUMERO_ORDEM = %s
        ORDER BY
          s.PRODSAI_NIVEL99
        , s.PRODSAI_GRUPO
        , s.PRODSAI_ITEM
        , tam.ORDEM_TAMANHO
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)
