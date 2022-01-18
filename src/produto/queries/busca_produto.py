from pprint import pprint

from utils.functions.models import rows_to_dict_list


def busca_produto(cursor, filtro_inteiro, cor, roteiro=None, alternativa=None, colecao=None):
    filtro = ''
    for palavra in filtro_inteiro.split(' '):
        filtro += """--
              AND (  r.REFERENCIA LIKE '%{palavra}%'
                  OR r.DESCR_REFERENCIA LIKE '%{palavra}%'
                  OR r.RESPONSAVEL LIKE '%{palavra}%'
                  OR r.CGC_CLIENTE_9 LIKE '%{palavra}%'
                  OR c.NOME_CLIENTE LIKE '%{palavra}%'
                  OR c.FANTASIA_CLIENTE LIKE '%{palavra}%'
                  )
        """.format(palavra=palavra)

    filtro_cor = ''
    get_cor = ''
    if len(cor.strip()) == 0:
        get_cor = """--
            , '' COR
            , '' COR_DESC
        """
    else:
        get_cor = """--
            , cor.ITEM_ESTRUTURA COR
            , cor.DESCRICAO_15 COR_DESC
        """
    for palavra in cor.split(' '):
        filtro_cor += """--
              AND (  cor.ITEM_ESTRUTURA LIKE '%{palavra}%'
                  OR cor.DESCRICAO_15 LIKE '%{palavra}%'
                  )
        """.format(palavra=palavra)

    get_alternativa = ''
    get_roteiro = ''
    if roteiro is None and alternativa is None:
        get_alternativa = """--
            , 0 ALTERNATIVA
        """
        get_roteiro = """--
            , 0 ROTEIRO
        """
    else:
        get_alternativa = """--
            , ia.ALTERNATIVA_ITEM ALTERNATIVA
        """
        get_roteiro = """--
            , ro.NUMERO_ROTEIRO ROTEIRO
        """

    filtro_alternativa = ''
    if alternativa is not None and alternativa != '0':
        filtro_alternativa += """--
              AND ia.ALTERNATIVA_ITEM = {alternativa}
        """.format(alternativa=alternativa)

    filtro_roteiro = ''
    if roteiro is not None and roteiro != '0':
        filtro_roteiro += """--
              AND ro.NUMERO_ROTEIRO = {roteiro}
        """.format(roteiro=roteiro)

    filtro_colecao = ''
    if colecao is not None and colecao != '':
        filtro_colecao += f"""--
              AND r.COLECAO = {colecao}
        """
        
    sql = f"""
        SELECT
          rownum NUM
        , rr.NIVEL
        , rr.REF
        , rr.COR
        , rr.COR_DESC
        , rr.TIPO
        , rr.DESCR
        , rr.RESP
        , rr.CNPJ9
        , rr.CNPJ4
        , rr.CNPJ2
        , rr.CLIENTE
        , rr.ROTEIRO
        , rr.ALTERNATIVA
        , rr.COLECAO
        FROM (
        SELECT DISTINCT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA like 'A%' THEN 'PG'
          WHEN r.REFERENCIA like 'B%' THEN 'PB'
          WHEN r.REFERENCIA like 'Z%' THEN 'MP'
          ELSE 'MD'
          END TIPO
        , r.DESCR_REFERENCIA DESCR
        , r.RESPONSAVEL RESP
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , COALESCE(c.FANTASIA_CLIENTE, c.NOME_CLIENTE) CLIENTE
        , co.COLECAO || '-' || co.DESCR_COLECAO COLECAO
        {get_cor} -- get_cor
        {get_roteiro} -- get_roteiro
        {get_alternativa} -- get_alternativa
        FROM BASI_030 r
        LEFT JOIN BASI_140 co
          ON co.COLECAO = r.COLECAO 
        LEFT JOIN BASI_010 cor
          ON cor.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND cor.GRUPO_ESTRUTURA = r.REFERENCIA
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = r.CGC_CLIENTE_9
         AND c.CGC_4 = r.CGC_CLIENTE_4
         AND c.CGC_2 = r.CGC_CLIENTE_2
        LEFT JOIN MQOP_050 ro
          ON ro.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND ro.GRUPO_ESTRUTURA = r.REFERENCIA
        LEFT JOIN BASI_050 ia -- insumos de alternativa
          ON ia.NIVEL_COMP = r.NIVEL_ESTRUTURA
         AND ia.GRUPO_COMP = r.REFERENCIA
        WHERE r.NIVEL_ESTRUTURA = 1
          AND NOT r.DESCR_REFERENCIA LIKE '-%'
          AND r.RESPONSAVEL IS NOT NULL
          {filtro} -- filtro
          {filtro_cor} -- filtro_cor
          {filtro_roteiro} -- filtro_roteiro
          {filtro_alternativa} -- filtro_alternativa
          {filtro_colecao} -- filtro_colecao
        ORDER BY
          NLSSORT(r.REFERENCIA,'NLS_SORT=BINARY_AI')
        ) rr
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
