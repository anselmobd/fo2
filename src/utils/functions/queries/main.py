from pprint import pprint, pformat

from django.conf import settings

from utils.functions import debug


def sql_where(
    field,
    value,
    operation="=",
    conector="AND",
    quote=None,
    left_transform=None,
    right_transform=None,
    full_transform=None,
):

    def value_quoted(value):
        value_quoted = f"{quote}{value}{quote}"
        if right_transform:
            value_quoted = right_transform.format(value_quoted)
        return value_quoted

    def join1000(value):
        size = 999  # um a menos que 1000 apenas por margem de segurança
        values = []
        for chunk in range((len(value) // size) + 1):
            values.append(
                ", ".join([
                    f"{value_quoted(item)}"
                    for item in value[chunk*size:chunk*size+size]
                ])
            )
        return values

    if bool(field) and value is not None:
        if full_transform:
            left_transform = full_transform
            right_transform = full_transform
        if left_transform:
            field = left_transform.format(field)
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
                values = join1000(value)
                if "IN" not in operation.upper():
                    if operation == "=":
                        operation = "IN"
                    else:
                        operation = "NOT IN"
                tests = [
                    f"{field} {operation} ({values_row})"
                    for values_row in values
                ]
            else:
                tests = [
                    f"{field} {operation} {value_quoted(item)}"
                    for item in value
                ]
            or_tests = ' OR '.join(tests)
            return f"{conector} ({or_tests})"
        else:
            return f"{conector} {field} {operation} {value_quoted(value)}"
    return ""


def none_if(value, test):
    return None if value == test else value


def coalesce(value, test):
    return test if value is None else value


def sql_where_none_if(
    field,
    value,
    test="",
    operation="=",
    conector="AND",
    quote = None,
    left_transform=None,
    right_transform=None,
    full_transform=None,
):
    return sql_where(
        field,
        none_if(value, test),
        operation=operation,
        conector=conector,
        quote=quote,
        left_transform=left_transform,
        right_transform=right_transform,
        full_transform=full_transform,
    )


def debug_cursor_execute_prt_on():
    settings.DEBUG_CURSOR_EXECUTE_PRT = True


def debug_cursor_execute_prt_off():
    settings.DEBUG_CURSOR_EXECUTE_PRT = False


def debug_cursor_execute(
        cursor, sql, list_args=None, prt=None, exec=True
    ):
    if prt is None:
        prt=settings.DEBUG_CURSOR_EXECUTE_PRT
    info = []
    if settings.DEBUG_CURSOR_EXECUTE:
        info.append(
            "\n".join([
                f"-- {line}"
                for line
                in debug(depth=slice(2, None), prt=False, verbose=False)
            ])
        )
        if list_args:
            info.append(
                "\n".join([
                    f"-- arg[{idx}]={pformat(line)}"
                    for idx, line
                    in enumerate(list_args)
                ])
            )
    info.append(sql)
    statment = "\n".join(info)
    if prt:
        print(statment)
    if exec:
        cursor.execute(statment, list_args)
