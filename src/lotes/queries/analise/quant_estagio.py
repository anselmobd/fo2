from pprint import pprint

from utils.functions.models import rows_to_dict_list


def quant_estagio(
        cursor, estagio=None, ref=None, tipo=None, cor=None, tam=None,
        only=None, less=None, group=None, deposito=None):

    def monta_filtro(in_, estagios):
        filtro = ''
        if estagios is not None:
            lista_estagios = ''
            sep = ''
            for estagio in estagios:
                    lista_estagios += f'{sep}{str(estagio)}'
                    sep = ', '
            filtro = (
                f'AND l.CODIGO_ESTAGIO {in_} ({lista_estagios})')
        return filtro

    filtra_estagios = ' '.join([
        monta_filtro('IN', only),
        monta_filtro('NOT IN', less),
    ])

    filtra_estagio = ''
    if estagio is not None and estagio != '':
        filtra_estagio = """--
            AND l.CODIGO_ESTAGIO = {} """.format(estagio)

    filtra_ref = ''
    if ref is not None and ref != '':
        if '%' in ref:
            filtra_ref = """--
                AND l.PROCONF_GRUPO LIKE '{}' """.format(ref)
        else:
            filtra_ref = """--
                AND l.PROCONF_GRUPO = '{}' """.format(ref)

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = "AND l.PROCONF_SUBGRUPO = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = "AND l.PROCONF_ITEM = '{cor}'".format(cor=cor)

    filtro_deposito = ''
    if deposito is not None:
        filtro_deposito = f"AND o.DEPOSITO_ENTRADA = {deposito}"

    filtro_group = ''
    if group is not None:
        if group == 'o':
            filtro_group = ", o.ORDEM_PRODUCAO"
        elif group == 'op':
            filtro_group = """--
                , o.ORDEM_PRODUCAO
                , o.PEDIDO_VENDA"""

    filtro_tipo = ''
    if tipo is not None:
        if tipo == 'a':
            filtro_tipo = "AND l.PROCONF_GRUPO < 'A0000'"
        elif tipo == 'g':
            filtro_tipo = "AND l.PROCONF_GRUPO like 'A%'"
        elif tipo == 'b':
            filtro_tipo = "AND l.PROCONF_GRUPO like 'B%'"
        elif tipo == 'p':
            filtro_tipo = \
                "AND (l.PROCONF_GRUPO like 'A%' OR l.PROCONF_GRUPO like 'B%')"
        elif tipo == 'v':
            filtro_tipo = "AND l.PROCONF_GRUPO < 'C0000'"
        elif tipo == 'm':
            filtro_tipo = "AND l.PROCONF_GRUPO >= 'C0000'"

    sql = f"""
        SELECT
          sum(
            CASE WHEN (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) QUANT
        {filtro_group} -- filtro_group
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        FROM PCPC_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
          {filtro_deposito} -- filtro_deposito
        --  AND l.PERIODO_PRODUCAO = 1921
        --  AND l.ORDEM_CONFECCAO = 01866
          {filtra_estagio} -- filtra_estagio
          {filtra_estagios} -- filtra_estagios
          {filtra_ref} -- filtra_ref
          {filtro_tipo} -- filtro_tipo
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
        GROUP BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        HAVING
          sum((l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO)) > 0
        ORDER BY
          l.PROCONF_NIVEL99
        {filtro_group} -- filtro_group
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
