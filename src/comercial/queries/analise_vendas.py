import pandas as pd
from datetime import date
from pprint import pprint

from utils.functions import dec_months
from utils.functions.models import rows_to_dict_list_lower
from utils.functions.strings import join_non_empty

import produto.queries


class AnaliseVendas():

    sql_base = (
    """ WITH item_vendido AS
        ( SELECT
            nf.DATA_EMISSAO DT
          , r.COLECAO COL
          , r.CGC_CLIENTE_9 CNPJ9
          , inf.NIVEL_ESTRUTURA NIVEL
          , inf.GRUPO_ESTRUTURA REF
          , TRIM(LEADING '0' FROM (
              REGEXP_REPLACE(inf.GRUPO_ESTRUTURA, '[^0-9]', '')
            )) MODELO
          , inf.SUBGRU_ESTRUTURA TAM
          , tam.ORDEM_TAMANHO ORD_TAM
          , inf.ITEM_ESTRUTURA COR
          , sum(inf.QTDE_ITEM_FATUR) QTD
          FROM FATU_050 nf -- nota fiscal da Tussor - capa
          JOIN fatu_060 inf -- item de nf de saída
            ON inf.CH_IT_NF_CD_EMPR = nf.CODIGO_EMPRESA
           AND inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
           AND inf.CH_IT_NF_SER_NFIS = nf.SERIE_NOTA_FISC
          JOIN estq_005 t -- transação de estoque
            ON t.CODIGO_TRANSACAO = inf.TRANSACAO
          JOIN PEDI_080 nop -- natureza de operação
            ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
           AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
          LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
            ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
           AND fe.SITUACAO_ENTRADA = 1 -- ativa
          LEFT JOIN BASI_030 r -- ref
            on r.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
           AND r.REFERENCIA = inf.GRUPO_ESTRUTURA
          LEFT JOIN BASI_220 tam
            ON tam.TAMANHO_REF = inf.SUBGRU_ESTRUTURA
          WHERE 1=1
            -- apenas Tussor
            AND nf.CODIGO_EMPRESA = 1
            -- apenas produto produzido
            AND inf.NIVEL_ESTRUTURA = 1
            -- ou o faturamento tem uma transação de venda
            -- ou é o caso especial de remessa de residuo
            AND ( t.TIPO_TRANSACAO = 'V'
                OR nf.NATOP_NF_NAT_OPER = 900
                )
            -- não cancelada
            AND nf.COD_CANC_NFISC = 0
            -- utilizou natureza configurada como faturamento
            AND nop.faturamento = 1
            -- sem nota de devolução
            AND fe.DOCUMENTO IS NULL
          GROUP BY 
            nf.DATA_EMISSAO
          , r.COLECAO
          , r.CGC_CLIENTE_9
          , inf.NIVEL_ESTRUTURA
          , inf.GRUPO_ESTRUTURA
          , inf.SUBGRU_ESTRUTURA
          , tam.ORDEM_TAMANHO
          , inf.ITEM_ESTRUTURA
        )
    """)

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
    agreg_fields = (
    """ , MIN(iv.DT) DT_MIN
        , MAX(iv.DT) DT_MAX
        , SUM(iv.QTD) QTD
    """)
    periodo_fields = ""
    group_fields = select_fields
    order_fields = select_fields

    infor_dict = {
        'ref': {
            'select_fields': (
                """iv."REF"
                """),
            'group_fields': ('select_fields', ),
            'order_fields': ('select_fields', ),
        },
        'modelo': {
            'select_fields': (
                """iv.MODELO
                """),
            'group_fields': ('select_fields', ),
            'order_fields': ('select_fields', ),
        },
        'tam': {
            'select_fields': (
                """iv.TAM
                """),
            'group_fields': (
                """   iv.TAM
                    , iv.ORD_TAM   
                """),
            'order_fields': 'iv.ORD_TAM',
        },
    }        

    ordem_dict = {
        'infor': '',
        'qtd': 'sum(iv.QTD) DESC',
    }        

    result = None

    def __init__(
        self, cursor, ref=None, modelo=None,
        infor=None, ordem=None,
        periodo_cols=None, qtd_por_mes=False):

        self.hoje = date.today()
        self.ini_mes = self.hoje.replace(day=1)

        self.referencias = []

        self.cursor = cursor
        self.qtd_por_mes = qtd_por_mes
        self.ordem = ordem

        self.ref = ref
        self.modelo = modelo
        self.infor = infor
        self.periodo_cols = periodo_cols

    def _set_ref(self, value):
        if value:
            if isinstance(value, list):
                self.referencias += value
            else:
                self.referencias.append(value)

    ref = property(fset=_set_ref)
    del _set_ref

    def _set_modelo(self, value):
        if value:
            self.ref = produto.queries.refs_de_modelo(self.cursor, value, tipo='pa')

    modelo = property(fset=_set_modelo)
    del _set_modelo

    def _set_infor(self, selecao):

        if selecao:
            first_infor = list(self.infor_dict)[0]
            sql_fields = self.infor_dict[first_infor].keys()

            for sql_field in sql_fields:
                info_sql = self.infor_dict[selecao][sql_field]

                if isinstance(info_sql, tuple):
                    sql_field_aux = info_sql[0]
                    info_sql = self.infor_dict[selecao][sql_field_aux]

                if sql_field == "order_fields":
                    info_sql = self.add_to_order_fields(info_sql)

                setattr(self, sql_field, info_sql)

    infor = property(fset=_set_infor)
    del _set_infor

    def _set_periodo_cols(self, value):
        if value:
            data_de, data_ate = self.limites_de_periodo_cols(value)
            self.filtra_periodo_data('>=', data_de)
            self.filtra_periodo_data('<', data_ate)
            self.monta_periodo_fields(value)

    periodo_cols = property(fset=_set_periodo_cols)
    del _set_periodo_cols

    def add_to_order_fields(self, info_sql):
        return join_non_empty(
            " , ",
            [
                self.ordem_dict[self.ordem],
                info_sql
            ]
        )

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
                if not final or int(lim_fim) < int(final):
                    final = lim_fim
        data_de = self.mes_to_timestamp(inicial)
        data_ate = self.mes_to_timestamp(final)
        return data_de, data_ate

    def mes_to_timestamp(self, mes):
        if mes:
            data = dec_months(self.ini_mes, int(mes))
            return f"TIMESTAMP '{data.strftime('%Y-%m-%d')} 00:00:00'"
        return ''

    def filtra_periodo_data(self, comparacao, data):
        if data:
            self.filtra_periodos += (
                f"""AND iv.DT {comparacao} {data}
                """
            )

    def monta_periodo_fields(self, periodo_cols):
        for coluna in periodo_cols:
            periodo = periodo_cols[coluna]

            lim_ini, lim_fim = tuple(periodo.split(':'))
            data_ini = dec_months(self.ini_mes, int(lim_ini))
            filtro = (
                f"""iv.dt >= TIMESTAMP '{data_ini.strftime('%Y-%m-%d')} 00:00:00'
                """    
            )

            if lim_fim != '':
                data_fim = dec_months(self.ini_mes, int(lim_fim))
                filtro += (
                    f"""AND iv.dt < TIMESTAMP '{data_fim.strftime('%Y-%m-%d')} 00:00:00'
                    """    
                )
            
            if self.qtd_por_mes:
                if lim_fim == '':
                    meses = self.diff_fmonth(data_ini, self.hoje)
                else:
                    meses = self.diff_fmonth(data_ini, data_fim)
                if meses < 1:
                    meses = 1
                div_meses = f" / {meses}"
            else:
                div_meses = ""

            self.periodo_fields += (
                f""", TRUNC(
                        SUM(
                          CASE WHEN {filtro} THEN iv.QTD
                          ELSE 0
                          END
                        )
                      {div_meses} ) {str2col_name(coluna)}
                """
            )

    def diff_fmonth(self, d1, d2):
        return (
            (d2.year - d1.year) * 12 +
            (d2.month - d1.month) +
            (d2.day - d1.day) / 30.5
        )

    def field_to_date(self, row, field):
        if field in row:
            row[field] = row[field].date()

    def calc_qtd_mes(self, row):
        if 'dt_min' in row and 'dt_max' in row:
            row['meses'] = round(
                self.diff_fmonth(
                    row['dt_min'],
                    row['dt_max']
                ),
                1
            )
            if row['meses'] < 1:
                row['meses'] = 1
        if 'qtd' in row and 'meses' in row:
            row['qtd_mes'] = int(
                row['qtd'] / row['meses']
            )

    def ajuste_fields(self, data):
        for row in data:
            self.field_to_date(row, 'dt')
            self.field_to_date(row, 'dt_min')
            self.field_to_date(row, 'dt_max')
            if self.qtd_por_mes:
                self.calc_qtd_mes(row)
                
    @property
    def filtra_ref(self):
        if self.referencias:
            refs = ", ".join(
                [f"'{r}'" for r in self.referencias]
            )
            return f" AND iv.REF IN ({refs})"
        return ""

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
              {self.agreg_fields} -- agreg_fields
              {self.periodo_fields} -- periodo_fields
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
            self.ajuste_fields(self.result)
        return self.result

    @property
    def df(self):
        if not self.result:
            self.cursor.execute(self.sql)
            columns = [i[0].lower() for i in self.cursor.description]
            self.result = pd.DataFrame(self.cursor, columns=columns)
            self.ajuste_fields(self.result)
        return self.result


def str2col_name(texto, ini='f'):
    name = ini
    append = False
    for c in texto:
        if c.isalnum():
            name += c.lower()
            append = True
        else:
            if append:
                name += '_'
                append = False
    return name
