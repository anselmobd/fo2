import pandas as pd
from datetime import date
from pprint import pprint

from utils.functions import dec_months
from utils.functions.models import rows_to_dict_list_lower


class AnaliseVendas():

    sql_base = (
    """ WITH item_vendido AS
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
    filtra_ref = ''
    filtra_periodos = ''
    select_fields = (
    """   iv.DT
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
    result = None

    def __init__(
        self, cursor, ref=None, por=None, periodo_cols=None):
        self.cursor = cursor
        self.ref = ref
        self.por = por
        self.periodo_cols = periodo_cols

    def _set_ref(self, value):
        if value:
            self.filtra_ref = f"AND iv.REF = '{value}'"

    ref = property(fset=_set_ref)
    del _set_ref

    def filtra_periodo_data(self, comparacao, data):
        if data:
            self.filtra_periodos += (
                f"""AND iv.DT {comparacao} {data}
                """
            )

    def _set_periodo_cols(self, value):
        if value:
            data_de, data_ate = self.limites_de_periodo_cols(value)
            self.filtra_periodo_data('>=', data_de)
            self.filtra_periodo_data('<', data_ate)

    periodo_cols = property(fset=_set_periodo_cols)
    del _set_periodo_cols

    def limites_de_periodo_cols(self, periodo_cols):
        periodos = list(periodo_cols.values())
        inicial = ''
        final = ''
        for periodo in periodos:
            lim_ini, lim_fim = tuple(periodo.split(':'))
            if lim_ini:
                if not inicial or int(lim_ini) > int(inicial):
                    inicial = lim_ini
            if lim_fim:
                if not final or int(lim_fim) > int(final):
                    final = lim_fim
        data_de = self.mes_to_timestamp(inicial)
        data_ate = self.mes_to_timestamp(final)
        return data_de, data_ate

    def mes_to_timestamp(self, mes):
        if mes:
            hoje = date.today()
            ini_mes = hoje.replace(day=1)
            data = dec_months(ini_mes, int(mes))
            return f"TIMESTAMP '{data.strftime('%Y-%m-%d')} 00:00:00'"
        return ''

    @property
    def filtros(self):
        return (
            f"""{self.filtra_ref} -- filtra_ref
                {self.filtra_periodos} -- filtra_periodos
            """
        )

    @property
    def sql(self):
        return (
            f"""{self.sql_base} -- sql_base
            SELECT 
              {self.select_fields} -- select_fields
              {self.sum_fields} -- sum_fields
            FROM item_vendido iv
            WHERE 1=1
              {self.filtros} -- filtros
            GROUP BY
              {self.group_fields} -- group_fields
            ORDER BY
              {self.order_fields} -- order_fields
        """)

    @property
    def data(self):
        if not self.result:
            self.cursor.execute(self.sql)
            self.result = rows_to_dict_list_lower(self.cursor)
        return self.result

    @property
    def df(self):
        if not self.result:
            self.cursor.execute(self.sql)
            columns = [i[0].lower() for i in self.cursor.description]
            self.result = pd.DataFrame(self.cursor, columns=columns)
        return self.result


def analise_vendas(cursor, ref=None, por=None, periodo_cols=None):
  
    def mes_to_timestamp(mes):
        if mes:
            hoje = date.today()
            ini_mes = hoje.replace(day=1)
            data = dec_months(ini_mes, int(mes))
            return f"TIMESTAMP '{data.strftime('%Y-%m-%d')} 00:00:00'"
        return ''

    def limites(periodo_cols):
        periodos = list(periodo_cols.values())
        inicial = ''
        final = ''
        for periodo in periodos:
            lim_ini, lim_fim = tuple(periodo.split(':'))
            if lim_ini:
                if not inicial or int(lim_ini) > int(inicial):
                    inicial = lim_ini
            if lim_fim:
                if not final or int(lim_fim) > int(final):
                    final = lim_fim
        data_de = mes_to_timestamp(inicial)
        data_ate = mes_to_timestamp(final)
        return data_de, data_ate

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

    # filtros
    filtra_ref = ""
    if ref is not None:
        filtra_ref = f"AND iv.REF = '{ref}'"

    filtra_periodos = ""
    if periodo_cols is not None:
        data_de, data_ate = limites(periodo_cols)
        if data_de:
            filtra_periodos += (
            f"""AND iv.DT >= {data_de}
            """)
        if data_ate:
            filtra_periodos += (
            f"""AND iv.DT < {data_ate}
            """)

    filtros = (
    f"""{filtra_ref} -- filtra_ref
        {filtra_periodos} -- filtra_periodos
    """)

    # retorno
    select_fields = (
    """   iv.DT
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
          {filtros} -- filtros
        GROUP BY
          {group_fields} -- group_fields
        ORDER BY
          {order_fields} -- order_fields
    """

    cursor.execute(sql)
    cached_result = rows_to_dict_list_lower(cursor)
    return cached_result
