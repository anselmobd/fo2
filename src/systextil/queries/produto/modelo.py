from pprint import pprint

from utils.functions.queries import sql_where, sql_where_none_if


def sql_custom_modelo_ref(field, alias="",type=str):
    if type == str:
        conv_ini = "TRIM(LEADING '0' FROM ("
        conv_fim = "))"
    else:
        conv_ini = "TO_NUMBER("
        conv_fim = ")"
    return f"""{conv_ini}REGEXP_REPLACE({field}, '[^0-9]', ''){conv_fim} {alias}"""


def sql_modelostr_ref(field):
    return sql_custom_modelo_ref(field, type=str)


def sql_modeloint_ref(field):
    return sql_custom_modelo_ref(field, type=int)


def sql_sele_modelostr_ref(field, alias='MODELO'):
    return sql_custom_modelo_ref(
        field, alias=alias, type=str)


def sql_sele_modeloint_ref(field, alias='MODELO'):
    return sql_custom_modelo_ref(
        field, alias=alias, type=int)


def sql_where_modelo_ref(field, modelo, operation="=", conector="AND"):
    return sql_where(
        sql_modelostr_ref(field),
        str(modelo),
        operation=operation,
        conector=conector,
    )
