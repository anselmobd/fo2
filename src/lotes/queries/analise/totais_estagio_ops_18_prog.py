from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list

from utils.functions import my_make_key_cache, fo2logger


def totais_estagio_ops_18_prog(cursor):
    key_cache = my_make_key_cache('totais_estagio_ops_18_prog')

    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    sql = """
        WITH
          op_est AS
        ( SELECT DISTINCT 
            l.ORDEM_PRODUCAO
          , o.ORDEM_PRINCIPAL
          , CASE WHEN l.CODIGO_ESTAGIO IN (3, 6, 22) THEN 3
            ELSE l.CODIGO_ESTAGIO
            END CODIGO_ESTAGIO
          , CASE WHEN l.PROCONF_GRUPO < 'C0000' THEN 'P'
            ELSE 'M'
            END TIPO_PRODUTO
          FROM PCPC_040 l
          JOIN PCPC_020 o
            ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          WHERE o.SITUACAO in (4, 2) -- Ordens em produção, Ordem confec. gerada
            AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
        )
        , op_pa_18 AS 
        ( SELECT 
            oe.ORDEM_PRODUCAO
          , count(*) pa_ests
          , max(oe.CODIGO_ESTAGIO) max_pa_est
          FROM op_est oe
          WHERE oe.TIPO_PRODUTO = 'P'
          GROUP BY 
            oe.ORDEM_PRODUCAO
          HAVING
            count(*) = 1
            AND max(oe.CODIGO_ESTAGIO) = 18
        )
        , op_md_ini AS 
        ( SELECT 
            oe.ORDEM_PRODUCAO
          , oe.ORDEM_PRINCIPAL
          , count(*) md_ests
          , max(oe.CODIGO_ESTAGIO) max_md_est
          FROM op_est oe
          WHERE oe.TIPO_PRODUTO = 'M'
          GROUP BY 
            oe.ORDEM_PRODUCAO
          , oe.ORDEM_PRINCIPAL
          HAVING
            count(*) = 1
            AND max(oe.CODIGO_ESTAGIO) = 3
        )
        SELECT 
          pa.ORDEM_PRODUCAO
        FROM op_pa_18 pa
        JOIN op_md_ini md
          ON md.ORDEM_PRINCIPAL = pa.ORDEM_PRODUCAO
    """
    cursor.execute(sql)

    cached_result = rows_to_dict_list(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
