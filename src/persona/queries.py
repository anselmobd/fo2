from pprint import pprint

from fo2.models import rows_to_dict_list_lower


def aniversariantes(cursor, mes):
    sql = """
        SELECT
          EXTRACT(MONTH FROM t.datanascimento) mes
        , EXTRACT(day FROM t.datanascimento) dia
        , INITCAP( t.nome ) nome
        , INITCAP( d.nome ) setor
        FROM persona.trabalhadores t
        join persona.mudancastrabalhadores mt
          on mt.trabalhador = t.trabalhador
        join persona.departamentos d
          on d.departamento = mt.departamento
        where t.datarescisao is null
          and ( t.vinculo = '10'
              or t.vinculo = '55' )
          and mt.departamento is not null
          and mt.datafinal is null
          and EXTRACT(MONTH FROM t.datanascimento) = %s
        ORDER by
          1
        , 2
        , t.nome
    """
    cursor.execute(sql, [mes])
    return rows_to_dict_list_lower(cursor)


def trabalhadores(cursor, codigo=None):
    filtra_codigo = ''
    if codigo is not None:
        filtra_codigo = f"AND t.codigo = '{codigo}'"

    sql = f"""
        select
          t.codigo
        , t.nome
        , t.datanascimento nascimento
        , t.cpf
        --, t.*
        FROM persona.trabalhadores t
        where t.datarescisao is null
          and ( t.vinculo = '10'
              or t.vinculo = '55' )
          {filtra_codigo} -- filtra_codigo
        order by
          t.codigo
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
