from pprint import pprint


def sql_where(field, value, operation="=", conector="AND", quote = ""):
    if bool(field) and value is not None:
        if not quote and isinstance(value, str):
            quote = "'"
        return f"{conector} {field} {operation} {quote}{value}{quote}"
    return ""


def none_if(value, test):
    return None if value == test else value
