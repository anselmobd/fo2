from pprint import pprint

from utils.functions import debug


def sql_where(field, value, operation="=", conector="AND", quote = None):
    if bool(field) and value is not None:
        if quote is None:
            if isinstance(value, tuple):
                test_value = value[0]
            else:
                test_value = value
            if isinstance(test_value, str):
                quote = "'"
            else:
                quote = ""
        if isinstance(value, tuple):
            if operation.upper() in ("=", "<>", "IN", "NOT IN"):
                values = ", ".join([
                    f"{quote}{item}{quote}"
                    for item in value
                ])
                if "IN" not in operation.upper():
                    if operation == "=":
                        operation = "IN"
                    else:
                        operation = "NOT IN"
                return f"{conector} {field} {operation} ({values})"
                
            else:
                tests = []
                for item in value:
                    tests.append(f"{field} {operation} {quote}{item}{quote}")
                or_tests = ' OR '.join(tests) 
                return f"{conector} ({or_tests})"
        else:
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


def debug_cursor_execute(cursor, sql, prt=False):
    statment = "\n".join([
        f"-- {line}"
        for line
        in debug(depth=slice(2, None), prt=False)
    ])
    statment += sql
    if prt:
        print(statment)
    cursor.execute(statment)
