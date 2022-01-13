from pprint import pprint


def sql_where(field, value, operation="=", conector="AND", quote = None):
    if bool(field) and value is not None:
        if quote is None:
            if isinstance(value, str):
                quote = "'"
            else:
                quote = ""
        return f"{conector} {field} {operation} {quote}{value}{quote}"
    return ""


def none_if(value, test):
    return None if value == test else value


def coalesce(value, test):
    return test if value is None else value


def sql_where_none_if(field, value, test, operation="=", conector="AND", quote = None):
    return sql_where(
        field,
        none_if(value, test),
        operation=operation,
        conector=conector,
        quote=quote,
    )
