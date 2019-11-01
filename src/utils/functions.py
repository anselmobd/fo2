import sys
import datetime
import inspect
import time
import logging
import inspect
import hashlib


fo2logger = logging.getLogger('fo2')


def arg_def(kwargs, arg, default):
    if arg in kwargs:
        return kwargs[arg]
    return default


__dow_info = {
    0: {'name': 'segunda-feira', 'plural': 'segundas-feiras',
        'alias': 'segunda', 'abb': 'seg'},
    1: {'name': 'terça-feira', 'plural': 'terças-feiras',
        'alias': 'terça', 'abb': 'ter'},
    2: {'name': 'quarta-feira', 'plural': 'quartas-feiras',
        'alias': 'quarta', 'abb': 'qua'},
    3: {'name': 'quinta-feira', 'plural': 'quintas-feiras',
        'alias': 'quinta', 'abb': 'qui'},
    4: {'name': 'sexta-feira', 'plural': 'sextas-feiras',
        'alias': 'sexta', 'abb': 'sex'},
    5: {'name': 'sábado', 'plural': 'sábados',
        'alias': 'sábado', 'abb': 'sab'},
    6: {'name': 'domingo', 'plural': 'domingos',
        'alias': 'domingo', 'abb': 'dom'},
}


def dow_info(dt, info, capitalize=False):
    dow = dt.weekday()
    result = __dow_info[dow][info]
    if capitalize:
        result = result.capitalize()
    return result


def inc_month(dt, months):
    newmonth = (((dt.month - 1) + months) % 12) + 1
    newyear = dt.year + (((dt.month - 1) + months) // 12)
    newday = dt.day
    newdt = None
    while newdt is None:
        try:
            newdt = datetime.date(newyear, newmonth, newday)
        except ValueError:
            newday -= 1
    return newdt


def dec_month(dt, day=None):
    if day is None:
        day = dt.day
    dt = dt.replace(day=1)
    dt = dt - datetime.timedelta(days=1)
    for _ in range(4):
        try:
            dt_return = dt.replace(day=day)
            break
        except Exception:
            day -= 1
    return dt_return


def dec_months(dt, number, day=None):
    if day is None:
        day = dt.day
    if number == 0:
        return dt.replace(day=day)
    dt_return = dec_month(dt, day)
    if number == 1:
        return dt_return
    else:
        return dec_months(dt_return, number-1, day)


def dias_uteis_mes():
    hoje = datetime.date.today()
    mes = hoje.month
    um_dia = datetime.timedelta(days=1)

    uteis_passados = 0
    util_hoje = 0
    uteis_total = 0
    dia = hoje.replace(day=1)
    while True:
        if mes != dia.month:
            break
        dow = dia.weekday()
        if dow < 5:
            uteis_total += 1
            if dia < hoje:
                uteis_passados += 1
            if dia == hoje:
                util_hoje = 1
        dia = dia + um_dia
    return uteis_total, uteis_passados, util_hoje


def shift_years(years, from_date=None):
    if from_date is None:
        from_date = datetime.datetime.now()
    try:
        return from_date.replace(year=from_date.year + years)
    except ValueError:
        # Must be 2/29!
        return from_date.replace(month=2, day=28,
                                 year=from_date.year + years)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def segunda(dt):
    if dt:
        return dt + datetime.timedelta(days=-dt.weekday())
    else:
        return None


def max_not_None(*args):
    maxi = None
    for v in args:
        if v:
            if maxi:
                maxi = max(
                    maxi,
                    v)
            else:
                maxi = v
    return maxi


def min_not_None(*args):
    mini = None
    for v in args:
        if v:
            if mini:
                mini = min(
                    mini,
                    v)
            else:
                mini = v
    return mini


def debug(message, level=None, depth=1):
    callerframerecord = inspect.stack()[depth]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    if level is None:
        level = 0
    msg = ''
    if level >= 3:
        msg += 'file={filename}-'
    if level >= 2:
        msg += 'func={function}-'
    if level >= 1:
        msg += 'line={line}-'
    msg += '{message}'
    print(
        msg.format(
            filename=info.filename,
            function=info.function,
            line=info.lineno,
            message=message,
            )
        )
    sys.stdout.flush()


def line_tik():
    debug(int(round(time.time() * 1000))/1000, 1, depth=2)


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False


def make_key_cache():
    stack1 = inspect.stack()[1]
    argvalues = inspect.getargvalues(stack1.frame).locals.values()
    values = []
    for value in argvalues:
        if value is None:
            values.append(value)
        elif isinstance(value, str):
            values.append(value)
        elif is_number(value):
            values.append(value)
    braces = ['{}'] * len(values)
    key = '|'.join([stack1.filename, *braces])
    key = key.format(*values)
    fo2logger.info(key)
    key = hashlib.md5(key.encode('utf-8')).hexdigest()
    key = '_'.join([stack1.function, key])
    return key
