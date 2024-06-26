from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import only_digits


class LotesEmEstoque():

    def __init__(
        self,
        cursor,
        tipo=None,
        ref=None,
        get=None,
        colecao=None,
        modelo=None,
        fields_tuple=None,
        lote=None,
        endereco=None,
        op=None,
        cor=None,
        tam=None,
    ):
        self.cursor = cursor
        self.tipo = tipo
        self.ref = ref
        self.get = get
        self.colecao = colecao
        self.modelo = modelo
        self.fields_tuple = fields_tuple
        self.lote = lote
        self.endereco = endereco
        self.op = op
        self.cor = cor
        self.tam = tam

        self.sql_em_stq = SqlEmEstoque(
            tipo=self.tipo,
            ref=self.ref,
            get=self.get,
            colecao=self.colecao,
            fields_tuple=self.fields_tuple,
            lote=self.lote,
            endereco=self.endereco,
            op=self.op,
            cor=self.cor,
            tam=self.tam,
        )

    def dados(self):
        sql = self.sql_em_stq.sql()

        debug_cursor_execute(self.cursor, sql)
        dados = dictlist_lower(self.cursor)

        if self.modelo:
            dados_modelo = []
        for row in dados:
            try:
                ref_modelo = int(only_digits(row['ref']))
            except ValueError:
                ref_modelo = 0
            row['modelo'] = ref_modelo
            if ref_modelo == self.modelo:
                dados_modelo.append(row)
        if self.modelo:
            return dados_modelo
        else:
            return dados


class SqlEmEstoque():
    """Monta SQL base de selecão de lotes
    - endereçados; e
    - no estágio 63
    Recebe:
    tipo
        i = inventário: todos os lotes endereçados e com quantidade no estágio 63
        p = lotes que aparece no inventário (opção acima) e são de OPs de Pedidos
        s = solicitado (situação 2, 3 ou 4) de OP com estágio 63
        iq = inventário: todos os lotes endereçados e com quantidade em qq estágio
        in = inventário: todos os lotes endereçados e com quantidade não no estágio 63
        None = todos os lotes
    ref: filtro de referências, caso não None
        iterable = uma lista de cond_expr
        string = cond_expr[, cond_expr]
            É transformada em uma lista de cond_expr
        Obs.:
            cond_expr = [condição] valor = filtro de uma referência
            condição: altera o funcionamento do filtro
                None = igualdade
                Várias condições válidas no SQL como '<', '>', '>='...
    get
        ref = busca apenas o campo referência (com distinct)
        None = busca apenas o campo referência (sem distinct)
        lote_qtd = busca op, lote, item e quantidades
        # loc = busca op, lote, item, quantidades e informação de endereçamento
    sinal: positivo ou negativo
        '+' = quantidades como estão no banco de dados
        '-' = inverte o sinal das quantidades       
    fields_tuple
        Lista de fields que devem ser retornados
        Field pode ter alias a ser utilizado. Ex.: "qtd quanti"
        obs.: ref sempre é retornado
    """

    def __init__(
        self, 
        tipo=None, 
        ref=None, 
        get=None, 
        colecao=None, 
        sinal='+', 
        fields_tuple=None,
        lote=None,
        endereco=None,
        op=None,
        cor=None,
        tam=None,
    ):
        self.tipo = tipo
        self.ref = ref
        self.get = get
        self.colecao = colecao
        self.sinal = sinal
        self.fields_tuple = fields_tuple
        self.lote = lote
        self.endereco = endereco
        self.op = op
        self.cor = cor
        self.tam = tam

        self.available_fields = {
            'ref': "l.PROCONF_GRUPO",
            'per': "l.PERIODO_PRODUCAO",
            'oc': "l.ORDEM_CONFECCAO",
            'lote': "lp.ORDEM_CONFECCAO",
            'palete': """--
                CASE
                  WHEN lp.COD_CONTAINER IS NOT NULL
                   AND lp.COD_CONTAINER <> '0'
                  THEN lp.COD_CONTAINER
                  ELSE '-'
                END
            """,
            'tam': "l.PROCONF_SUBGRUPO",
            'ordem_tam': "tam.ORDEM_TAMANHO",
            'cor': "l.PROCONF_ITEM",
            'op': "l.ORDEM_PRODUCAO",
            'qtd_prog': "l.QTDE_PECAS_PROG",
            'qtd_dbaixa': "l.QTDE_DISPONIVEL_BAIXA",
            'rota': "COALESCE(e.ROTA, '-')",
            'endereco': "COALESCE(ec.COD_ENDERECO, '-')",
            'estagio': "COALESCE(l.CODIGO_ESTAGIO, 999)",
            'est_sol': """
                ( SELECT
                    MOD(( SELECT 
                            MAX(
                              CASE WHEN l2.CODIGO_ESTAGIO = 63 THEN 163
                              ELSE l2.CODIGO_ESTAGIO
                              END
                            )
                          FROM pcpc_040 l2
                          WHERE 1=1
                            AND l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                            AND l2.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                            AND l2.QTDE_DISPONIVEL_BAIXA > 0
                        )
                    , 100
                    )
                  FROM dual
                )
            """,
            'solicitacoes': """--
                COALESCE(
                  ( SELECT
                      LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                      WITHIN GROUP (ORDER BY sl.SOLICITACAO) colicitacoes
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                  ),
                '-'
                )
            """,
            'qtd_sol': """--
                COALESCE(
                  ( SELECT
                      SUM(sl.QTDE) qtd_sol
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                      AND sl.SOLICITACAO IS NOT NULL
                      AND sl.SOLICITACAO > 0
                  ),
                0
                )
            """,
            'qtd_emp': """--
                COALESCE(
                  ( SELECT
                      SUM(sl.QTDE) qtd_sol
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                      AND (
                        sl.SOLICITACAO IS NULL
					    OR sl.SOLICITACAO = 0
					  )
                  ),
                0
                )
            """,
        }

    def condicao_valor(self, ref):
        if len(ref.split()) == 2:
            condicao = ref.split()[0]
            ref = str(ref.split()[1])
        else:
            condicao = '='
        return condicao, ref

    def sql(self):
        filter_ref = ''
        ref_conds = []
        ref_in = []
        if isinstance(self.ref, str):
            self.ref = map(
                str.strip,
                self.ref.split(','),
            )
        if self.ref is not None:  # iterable
            for r in self.ref:
                condicao, valor = self.condicao_valor(r)
                if condicao == '=':
                    ref_in.append(valor)
                else:
                    ref_conds.append(f"l.PROCONF_GRUPO {condicao} '{valor}'")
        if ref_in:
            refs = ', '.join([f"'{r}'" for r in ref_in])
            ref_conds.append(f"l.PROCONF_GRUPO in ({refs})")
        if ref_conds:
            filters_ref = " AND ".join(ref_conds)
            filter_ref = f"AND {filters_ref}"

        join_para_colecao = ""
        filter_colecao = ""
        if self.colecao is not None:
            join_para_colecao = """
                JOIN BASI_030 r
                  ON r.NIVEL_ESTRUTURA = 1
                 AND r.REFERENCIA = l.PROCONF_GRUPO 
            """
            filter_colecao = f"AND r.COLECAO = '{self.colecao}'"

        filter_lote = ""
        if self.lote is not None:
            filter_lote = f"AND lp.ORDEM_CONFECCAO = '{self.lote}'"

        filter_endereco = ""
        if self.endereco is not None:
            filter_endereco = f"AND ec.COD_ENDERECO LIKE '{self.endereco}%'"

        filter_op = ""
        if self.op is not None:
            filter_op = f"AND l.ORDEM_PRODUCAO = '{self.op}'"

        filter_cor = ""
        if self.cor is not None:
            filter_cor = f"AND l.PROCONF_ITEM = '{self.cor}'"

        filter_tam = ""
        if self.tam is not None:
            filter_tam = f"AND l.PROCONF_SUBGRUPO = '{self.tam}'"

        self.fields_tuple = self.fields_tuple if self.fields_tuple else []
        fields_set = {'ref'}.union(self.fields_tuple)

        distinct = False
        if self.get == 'ref':
            distinct = True
        elif self.get == 'lote_qtd':
            fields_set = fields_set.union([
                'per',
                'oc',
                'tam',
                'ordem_tam',
                'cor',
                'op',
                'qtd_prog',
                'qtd_dbaixa',
            ])

        filtra_estagio = "AND l.CODIGO_ESTAGIO = 63"
        if self.tipo == 'p':
            field_qtd = f"""--
                , {self.sinal}l.QTDE_DISPONIVEL_BAIXA qtd
            """
            tipo_join = """--
                JOIN PCPC_020 op
                  ON op.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
            """
            tipo_filter = """--
                AND op.PEDIDO_VENDA <> 0
                AND l.QTDE_DISPONIVEL_BAIXA > 0
            """
        elif self.tipo == 's':
            field_qtd = f"""--
                , {self.sinal}sl.QTDE qtd
            """
            tipo_join = """--
                JOIN PCPC_044 sl
                  ON sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
                 AND sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000) 
            """
            tipo_filter = """--
                AND sl.SITUACAO IN (2, 3, 4)
            """
        elif self.tipo and self.tipo.startswith('i'):
            field_qtd = f"""--
                , {self.sinal}l.QTDE_DISPONIVEL_BAIXA qtd
            """
            tipo_join = ""
            tipo_filter = """--
                AND l.QTDE_DISPONIVEL_BAIXA > 0
            """
            if 'q' in self.tipo:
                filtra_estagio = ''
            elif 'n' in self.tipo:
                filtra_estagio = "AND l.CODIGO_ESTAGIO <> 63"
        else:
            field_qtd = ""
            tipo_join = ""
            tipo_filter = """--
                AND l.QTDE_DISPONIVEL_BAIXA > 0
            """

        fields = "\n, ".join(
            [
                f"{self.available_fields[field.split()[0]]} {field.split()[-1]}"
                for field in fields_set
            ]
        )

        sql = f"""
            SELECT {"DISTINCT" if distinct else ""}
            {fields} -- fields
            {field_qtd} -- field_qtd
            FROM ENDR_014 lp
            JOIN PCPC_040 l
              ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
             AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
            LEFT JOIN ENDR_015 ec -- endereço/container 
              ON ec.COD_CONTAINER = lp.COD_CONTAINER
            LEFT JOIN ENDR_013 e -- endereço
              ON e.COD_ENDERECO = ec.COD_ENDERECO
            {tipo_join} -- tipo_join
            {join_para_colecao} -- join_para_colecao
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            WHERE 1=1
            {filtra_estagio} -- filtra_estagio
            {tipo_filter} -- tipo_filter
            {filter_ref} -- filter_ref
            {filter_colecao} -- filter_colecao
            {filter_lote} -- filter_lote
            {filter_endereco} -- filter_endereco
            {filter_op} -- filter_op
            {filter_cor} -- filter_cor
            {filter_tam} -- filter_tam
        """
        return sql
