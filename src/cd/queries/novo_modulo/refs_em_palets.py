from itertools import cycle
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import split_numbers

from o2.functions.text import splited

from lotes.functions.varias import (
    lote_de_periodo_oc,
    modelo_de_ref,
    periodo_oc,
)

from cd.queries.novo_modulo.gerais import get_filtra_ref

__all__ = ['query']


def numbers_set(str):
    return set(split_numbers(str, negative=True))


def numbers_sets(str):
    nums = split_numbers(str, negative=True)
    return (
        set(num for num in nums if num[0] != "-"),
        set(num[1:] for num in nums if num[0] == "-"),
    )


fields_tuple = {
    'ref': ('ref', ),
    'op': (
        'op',
        'ref',
    ),
    'inv': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd',
    ),
    'emp': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd_emp qtd',
    ),
    'sol': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd_sol qtd',
    ),
    'all': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd',
        'qtd_emp',
        'qtd_sol',
    ),
    'detalhe': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd',
        'qtd_emp',
        'qtd_sol',
        'qtd_prog',
        'estagio',
        'est_sol',
        'solicitacoes',
        'palete',
        'palete_dt',
        'endereco',
        'rota',
    ),
    'detalhe+fin': (
        'op',
        'per',
        'oc',
        'ref',
        'ordem_tam',
        'tam',
        'cor',
        'qtd',
        'qtd_emp',
        'qtd_sol',
        'qtd_prog',
        'estagio',
        'est_sol',
        'solicitacoes',
        'palete',
        'palete_dt',
        'endereco',
        'rota',
        'sol_fin',
        'qtd_fin',
    ),
}


def query(
    cursor,
    fields='ref',
    ref=None,
    cor=None,
    tam=None,
    colecao=None,
    op=None,
    lote=None,
    per=None,
    oc=None,
    modelo=None,
    endereco=None,
    tipo_prod=None,
    situacao_empenho='t',
    paletizado='s',
    selecao_ops='63',
    selecao_lotes='63',
    corte_de=None,
    corte_ate=None,
    qtd_empenhada='t',
    qtd_solicitada='-',
    solicitacoes=None,
    verifica_sols_in=True,
    verifica_sols_out=True,
    modelos=None,
):
    """
    cursor: cursor de acesso ao BD
    fields: define os campos a serem buscados
        lista de campos (list ou tuple); ou
        'ref': busca apenas referências
        'op': busca apenas referências e OPs
        'inv': dados suficientes para grade de inventário
        'emp': dados suficientes para grade de empenhos (empenhos
               sem número de solicitação)
        'sol': dados suficientes para grade de solicitações (empenhos
               com número de solicitação)
        'all': dados suficientes para grades de inventário, empenhos
               e solicitações (empenhos com e sem número de solicitação)
        'detalhe': igual a 'all' mais informações sobre estágio, números
                   de solicitações e endereçamento
        'detalhe+fin': igual a 'detalhe' mais informações sobre
                       finalizados
    ref: filtra no BD por referência
        uma referência ou um list (ou tuple) de referências
    cor: filtra no BD por cor
        cor de referência
    tam: filtra no BD por tamanho
        tamanho de referência
    colecao: filtra no BD por coleção
        código de coleção de referência
    op: filtra no BD por op
        OP de lote
    lote: filtra no BD por lote
    solicitacoes: filtra LOCALMENTE
        string com lista de números de solicitações
        pode ter "-" antes do número
        filtra lotes que tem solicitações sem "-"
        e que não tem solicitações com "-"
    per: filtra no BD por período
        período de lote
    oc: filtra no BD por OC
        ordem de confecção de lote
    modelo: filtra no DB por referências de modelo com OP
            e LOCALMENTE por modelo
        modelo de referência
    endereco: filtra no BD por endereço do lote no CD, podendo ser uma
              ou mais ocorrencias, separadas por espaços, de:
        endereço do lote inteiro
        endereço do lote parcial (início)
        faixa (de-até)
        "*" significando endereço não nulo
    tipo_prod: filtra no DB por tipo de produto de acordo com
               características da referência
        pagb: PA/PG/PB
        pgb: PG/PB
        pa: PA
        pg: PG
        pb: PB
        md: MD
        todos: Todos os tipos
    paletizado: filtra no DB pelo palete
        s: Exige palete
        63: Exige palete apenas no 63
        n: Exige não ter palete
        t: Não filtra
    situacao_empenho:
        t: Não filtra
        esnf: Empenhado ou solicitado não finalizado
        es34: Empenhado ou solicitado não finalizado com situação 3 ou 4
        enf: Empenhado não finalizado
        snf: Solicitado não finalizado
        esf: Empenhado/solicitado finalizado
    qtd_empenhada:
        t: * Não filtra
        ce: Com empenho
        te: Totalmente empenhado
        nte: Não totalmente empenhado
        pe: Parcialmente empenhado
        se: Sem empenho
    qtd_solicitada:
        - ou None: Não filtra
        t: Solicitação total
        tp: Solicitação total ou parcial
        p: Solicitação parcial
        pn: Solicitação parcial ou não solicitado
        n: Não solicitado
    selecao_ops: filtra no BD OPs
        63: Com estágio 63 (CD)
        n63: Sem estágio 63 (CD)
        t: Não filtra
    selecao_lotes: filtra no BD lotes
        63 = lotes com quantidade no estágio 63
        qq = lotes com quantidade em qq estágio
        605763 = lotes com quantidade nos estágios 60, 57 ou 63
        n63 = lotes com quantidade não no estágio 63
        <63 = lotes com quantidade anterior ao estágio 63
        60 = lotes com quantidade no estágio 60
        57 = lotes com quantidade no estágio 57
        fin = lotes finalizados
        t: Não filtra
    modelos: filtra LOCALMENTE
        string com lista de modelos
        pode ter "-" antes do modelo
        filtra lotes que são dos modelos sem "-"
        e que não são dos modelos com "-"
    """
    joins = set()

    filtra_ref = get_filtra_ref(
        cursor,
        field="l.PROCONF_GRUPO",
        ref=ref,
        modelo=modelo,
        com_op=True,
    )

    filtra_cor = f"""--
        AND l.PROCONF_ITEM = '{cor}'
    """ if cor else ''

    filtra_tam = f"""--
        AND l.PROCONF_SUBGRUPO = '{tam}'
    """ if tam else ''

    filtra_colecao = ''
    if colecao:
        filtra_colecao = f"""
            AND r.COLECAO = '{colecao}'
        """
        joins.add('1r')

    filtra_op = f"""--
        AND l.ORDEM_PRODUCAO = '{op}'
    """ if op else ''

    filtra_corte_de = f"""--
        AND op.DATA_ENTRADA_CORTE >= DATE '{corte_de}'
    """ if corte_de else ''

    filtra_corte_ate = f"""--
        AND op.DATA_ENTRADA_CORTE <= DATE '{corte_ate}'
    """ if corte_ate else ''

    if lote:
         per, oc = periodo_oc(lote)

    filtra_per = f"""--
        AND l.PERIODO_PRODUCAO = '{per}'
    """ if per else ''

    filtra_oc = f"""--
        AND l.ORDEM_CONFECCAO = '{oc}'
    """ if oc else ''

    filtra_endereco = ''
    if endereco:
        end_list = splited(endereco)
        filtro_list = []
        for end in end_list:
            if len(end) == 6:
                filtra_end1 = f"""--
                    ec.COD_ENDERECO = '{end}'
                """
            elif '-' in end:
                end_de, end_ate = tuple(end.split('-'))
                filtra_end1 = f"""--
                    ( ec.COD_ENDERECO >= '{end_de}'
                    AND ec.COD_ENDERECO <= '{end_ate}' )
                """
            elif end == "*":
                filtra_end1 = """--
                    ec.COD_ENDERECO IS NOT NULL
                """
            else:
                filtra_end1 = f"""--
                    ec.COD_ENDERECO LIKE '{end}%'
                """
            filtro_list.append(filtra_end1)
        filtra_endereco = ' OR '.join(filtro_list)
        filtra_endereco = f"AND ({filtra_endereco})"
        joins.add('1ec')

    dict_tipo_prod = {
        'pagb': "AND l.PROCONF_GRUPO < 'C0000'",
        'pgb': "AND (l.PROCONF_GRUPO like 'A%' OR l.PROCONF_GRUPO like 'B%')",
        'pa': "AND l.PROCONF_GRUPO < 'A0000'",
        'pg': "AND l.PROCONF_GRUPO like 'A%'",
        'pb': "AND l.PROCONF_GRUPO like 'B%'",
        'md': "AND l.PROCONF_GRUPO >= 'C0000'",
    }

    filtra_tipo_prod = dict_tipo_prod[tipo_prod] if tipo_prod else ''

    filtra_selecao_ops = ''
    if selecao_ops == '63':
        filtra_selecao_ops = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_040 l2 -- lote
              WHERE l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND l2.CODIGO_ESTAGIO = 63
            )
        """
    elif selecao_ops == 'n63':
        filtra_selecao_ops = """--
            AND NOT EXISTS (
              SELECT
                1
              FROM pcpc_040 l2 -- lote
              WHERE l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND l2.CODIGO_ESTAGIO = 63
            )
        """

    filtra_selecao_lotes = ""
    if selecao_lotes == '63':
        filtra_selecao_lotes = """--
            AND l.CODIGO_ESTAGIO = 63
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == 'n63':
        filtra_selecao_lotes = """--
            AND l.CODIGO_ESTAGIO <> 63
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == '<63':
        filtra_selecao_lotes = """--
            AND l.SEQUENCIA_ESTAGIO < (
              SELECT
                MIN(l2.SEQUENCIA_ESTAGIO)
              FROM pcpc_040 l2 -- lote
              WHERE l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND l2.CODIGO_ESTAGIO = 63
            )
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == '60':
        filtra_selecao_lotes = """--
            AND l.CODIGO_ESTAGIO = 60
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == '57':
        filtra_selecao_lotes = """--
            AND l.CODIGO_ESTAGIO = 57
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == '605763':
        filtra_selecao_lotes = """--
            AND l.CODIGO_ESTAGIO in (60, 57, 63)
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == 'qq':
        filtra_selecao_lotes = """--
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif selecao_lotes == 'fin':
        filtra_selecao_lotes = """--
            AND l.SEQUENCIA_ESTAGIO = 1
            AND NOT EXISTS (
              SELECT
                1
              FROM pcpc_040 l2 -- lote
              WHERE l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND l2.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND l2.QTDE_DISPONIVEL_BAIXA > 0
            )
        """

    filtra_situacao_empenho = ''
    if situacao_empenho == 'esnf':
        filtra_situacao_empenho = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_044 sl -- solicitação / lote
              WHERE sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SITUACAO IN (1, 2, 3, 4)
            )
        """
    elif situacao_empenho == 'es34':
        filtra_situacao_empenho = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_044 sl -- solicitação / lote
              WHERE sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SITUACAO IN (3, 4)
            )
        """
    elif situacao_empenho == 'esf':
        filtra_situacao_empenho = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_044 sl -- solicitação / lote
              WHERE sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SITUACAO = 5
            )
        """
    elif situacao_empenho == 'enf':
        filtra_situacao_empenho = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_044 sl -- solicitação / lote
              WHERE sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SOLICITACAO IS NULL
                AND sl.SITUACAO IN (1, 2, 3, 4)
            )
        """
    elif situacao_empenho == 'snf':
        filtra_situacao_empenho = """--
            AND EXISTS (
              SELECT
                1
              FROM pcpc_044 sl -- solicitação / lote
              WHERE sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SOLICITACAO IS NOT NULL
                AND sl.SITUACAO IN (1, 2, 3, 4)
            )
        """

    filtra_paletizado = ''
    if paletizado == 's':
        filtra_paletizado = """--
            AND lp.COD_CONTAINER IS NOT NULL
            AND lp.COD_CONTAINER <> '0'
        """
    elif paletizado == '63':
        filtra_paletizado = """--
            AND (
              ( lp.COD_CONTAINER IS NOT NULL
                AND lp.COD_CONTAINER <> '0'
              )
              OR l.CODIGO_ESTAGIO <> 63
            )
        """
    elif paletizado == 'n':
        filtra_paletizado = """--
            AND (
              lp.COD_CONTAINER IS NULL
              OR lp.COD_CONTAINER = '0'
            )
        """

    if not isinstance(fields, (tuple, list)):
        fields = fields_tuple[fields]

    filtra_qtd_empenhada = ''
    if {'qtd', 'qtd_emp', 'qtd_sol'}.issubset(fields):
        dict_qtd_empenhada = {
            't': '',
            'ce': "AND (d.qtd_emp + d.qtd_sol) > 0",
            'te': "AND (d.qtd_emp + d.qtd_sol) >= d.qtd",
            'nte': "AND (d.qtd_emp + d.qtd_sol) < d.qtd",
            'pe': """--
                AND (d.qtd_emp + d.qtd_sol) > 0
                AND (d.qtd_emp + d.qtd_sol) < d.qtd
            """,
            'se': "AND (d.qtd_emp + d.qtd_sol) = 0",
        }
        filtra_qtd_empenhada = (
            dict_qtd_empenhada[qtd_empenhada] if qtd_empenhada else '')

    filtra_qtd_solicitada = ''
    if {'qtd', 'qtd_sol'}.issubset(fields):
        dict_qtd_solicitada = {
            '-': '',
            't': "AND d.qtd_sol >= d.qtd",
            'tp': "AND d.qtd_sol > 0",
            'p': """--
                AND d.qtd_sol > 0
                AND d.qtd_sol < d.qtd
            """,
            'pn': "AND d.qtd_sol < d.qtd",
            'n': "AND d.qtd_sol = 0",
        }
        filtra_qtd_solicitada = (
            dict_qtd_solicitada[qtd_solicitada] if qtd_solicitada else '')

    field_statement = {
        'ref': "l.PROCONF_GRUPO",
        'ordem_tam': "COALESCE(tam.ORDEM_TAMANHO, 0)",
        'tam': "l.PROCONF_SUBGRUPO",
        'op': "l.ORDEM_PRODUCAO",
        'qtd_prog': "l.QTDE_PECAS_PROG",
        'qtd_dbaixa': "l.QTDE_DISPONIVEL_BAIXA",
        'oc': "l.ORDEM_CONFECCAO",
        'per': "l.PERIODO_PRODUCAO",
        'estagio': """
            CASE
              WHEN l.QTDE_DISPONIVEL_BAIXA = 0
              THEN 0
              ELSE l.CODIGO_ESTAGIO
            END
        """,
        'cor': "l.PROCONF_ITEM",
        'qtd': "l.QTDE_DISPONIVEL_BAIXA",
        'palete': """--
            CASE
              WHEN lp.COD_CONTAINER IS NOT NULL
               AND lp.COD_CONTAINER <> '0'
              THEN lp.COD_CONTAINER
              ELSE '-'
            END
        """,
        'palete_dt': """--
            CASE
              WHEN lp.COD_CONTAINER IS NOT NULL
               AND lp.COD_CONTAINER <> '0'
              THEN lp.DATA_INCLUSAO
              ELSE NULL
            END
        """,
        'rota': "COALESCE(e.ROTA, '-')",
        'endereco': "COALESCE(ec.COD_ENDERECO, '-')",
        'est_sol': """
            ( SELECT
                MOD(
                  ( SELECT
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
                    WITHIN GROUP (ORDER BY sl.SOLICITACAO)
                FROM pcpc_044 sl -- solicitação / lote
                WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                    -- AND sl.ORDEM_CONFECCAO <> 0
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO IN (1, 2, 3, 4)
                    AND sl.QTDE <> 0
                ),
            '-'
            )
        """,
        'sol_fin': """--
            COALESCE(
                ( SELECT
                    LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                    WITHIN GROUP (ORDER BY sl.SOLICITACAO) colicitacoes
                FROM pcpc_044 sl -- solicitação / lote
                WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                    -- AND sl.ORDEM_CONFECCAO <> 0
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO = 5
                ),
            '-'
            )
        """,
        'qtd_emp': """--
            COALESCE(
                ( SELECT
                    SUM(sl.QTDE) qtd_emp
                  FROM pcpc_044 sl -- solicitação / lote
                  WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                    -- AND sl.ORDEM_CONFECCAO <> 0
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
        'qtd_sol': """--
            COALESCE(
                ( SELECT
                    SUM(sl.QTDE) qtd_sol
                  FROM pcpc_044 sl -- solicitação / lote
                  WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                    -- AND sl.ORDEM_CONFECCAO <> 0
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO IN (1, 2, 3, 4)
                    AND sl.SOLICITACAO IS NOT NULL
                    AND sl.SOLICITACAO > 0
                ),
                0
            )
        """,
        'qtd_fin': """--
            COALESCE(
                ( SELECT
                    SUM(sl.QTDE) qtd_fin
                  FROM pcpc_044 sl -- solicitação / lote
                  WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                    -- AND sl.ORDEM_CONFECCAO <> 0
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO = 5
                ),
                0
            )
        """,
    }

    field_join = {
        'ordem_tam': '1tam',
        'endereco': '1ec',
        'rota': '2e',
    }

    fields_statements_list = []
    for field in fields:
        field_part = cycle(field.split())
        fields_cod, field_alias = next(field_part), next(field_part)

        fields_statements_list.append(
            f"{field_statement[fields_cod]} {field_alias}"
        )

        if fields_cod in field_join:
            joins.add(field_join[fields_cod])

    fields_statements = "\n, ".join(fields_statements_list)

    join_statement = {
        '1r': """--
            JOIN BASI_030 r -- referencia
              ON r.NIVEL_ESTRUTURA = 1
             AND r.REFERENCIA = l.PROCONF_GRUPO
        """,
        '1tam': """--
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        """,
        '1ec': """--
            LEFT JOIN ENDR_015 ec -- endereço/container
              ON ec.COD_CONTAINER = lp.COD_CONTAINER
        """,
        '2e': """--
            LEFT JOIN ENDR_013 e -- endereço
              ON e.COD_ENDERECO = ec.COD_ENDERECO
        """,
    }

    joins_list = list(joins)
    joins_statements = "".join(
        [
            join_statement[join]
            for join in sorted(joins_list)
        ]
    )

    sql = f"""
        WITH dados AS (
        SELECT DISTINCT
          {fields_statements} -- fields_statements
        FROM PCPC_040 l
        JOIN PCPC_020 op
          ON op.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN ENDR_014 lp
          ON lp.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
         AND lp.ORDEM_CONFECCAO = (l.PERIODO_PRODUCAO * 100000) + l.ORDEM_CONFECCAO
        {joins_statements} -- joins_statements
        WHERE 1=1
          AND op.COD_CANCELAMENTO = 0
          {filtra_situacao_empenho} -- filtra_situacao_empenho
          {filtra_selecao_ops} -- filtra_selecao_ops
          {filtra_selecao_lotes} -- filtra_selecao_lotes
          {filtra_op} -- filtra_op
          {filtra_corte_de} -- filtra_corte_de
          {filtra_corte_ate} -- filtra_corte_ate
          {filtra_per} -- filtra_per
          {filtra_oc} -- filtra_oc
          {filtra_ref} -- filtra_ref
          {filtra_cor} -- filtra_cor
          {filtra_tam} -- filtra_tam
          {filtra_colecao} -- filtra_colecao
          {filtra_endereco} -- filtra_endereco
          {filtra_tipo_prod} -- filtra_tipo_prod
          {filtra_paletizado} -- filtra_paletizado
        )
        SELECT
          d.*
        FROM dados d
        WHERE 1=1
          {filtra_qtd_empenhada} -- filtra_qtd_empenhada
          {filtra_qtd_solicitada} -- filtra_qtd_solicitada
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['modelo'] = modelo_de_ref(row['ref'])
        if {'per', 'oc'}.issubset(fields):
            row['lote'] = lote_de_periodo_oc(row['per'], row['oc'])

    if modelo:
        dados = [
            row for row in dados
            if row['modelo'] == modelo
        ]

    if solicitacoes and 'solicitacoes' in fields:
        sols_in, sols_out = numbers_sets(solicitacoes)
        dados_solicitacoes = []
        for row in dados:
            if verifica_sols_in:
                solic_ok = (
                    numbers_set(row['solicitacoes']).intersection(sols_in) or
                    not sols_in
                )
            else:
                solic_ok = True
            if verifica_sols_out:
                solic_ok = (
                    solic_ok and
                    not numbers_set(row['solicitacoes']).intersection(sols_out)
                )
            if solic_ok:
                dados_solicitacoes.append(row)
        dados = dados_solicitacoes

    if modelos:
        mods_in, mods_out = numbers_sets(modelos)
        mods_in = list(map(int, mods_in))
        mods_out = list(map(int, mods_out))
        dados = [
            row for row in dados
            if (
                ((row['modelo'] in mods_in) or not mods_in)
                and (row['modelo'] not in mods_out)
            )
        ]

    return dados
