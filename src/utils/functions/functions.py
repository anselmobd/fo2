import datetime
import inspect
import logging
import hashlib
import sys
import time
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from pprint import pprint

from django.conf import settings
from django.utils.text import slugify

from utils.classes import AcessoInterno


fo2logger = logging.getLogger('fo2')

_cache_local = (
    settings.CACHES['default']['BACKEND'] ==
    'django.core.cache.backends.locmem.LocMemCache'
)


def loginfo(info, prt=settings.DEBUG_CURSOR_EXECUTE_PRT):
    fo2logger.info(info)
    if prt:
        print(info)


def arg_def(kwargs, arg, default):
    if arg in kwargs:
        return kwargs[arg]
    return default


def inc_mes(dt, months=1):
    return dt + relativedelta(months=months)


def inc_dias_mes_menos1(dt):
    return dt + datetime.timedelta(monthrange(dt.year, dt.month)[1] - 1)


def inc_month(dt, months=1):
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


def dias_mes_data(dt):
    prox_mes = inc_month(dt)
    ult_dia = prox_mes - datetime.timedelta(days=prox_mes.day)
    return ult_dia.day


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
    if hasattr(request, 'META'):
        dados = request.META
    else:
        dados = request
    x_forwarded_for = dados.get('HTTP_X_FORWARDED_FOR')
    addr = dados.get('REMOTE_ADDR')
    fo2logger.info(
        f'get_client_ip x_forwarded_for={x_forwarded_for} addr={addr}')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = addr
    return ip
    # client_ip, is_routable = ipware.get_client_ip(request)
    # # pprint([client_ip, is_routable])
    # return client_ip


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


def debug(message=None, level=0, depth=None, prt=True, verbose=True):
    if depth is None:
        depth = slice(1,None)
    if isinstance(depth, int):
        depth = slice(depth, depth+1)
    if not prt:
        lines = []
    for callerframerecord in inspect.stack()[depth]:
        line = debug_line(
            callerframerecord, message, level, verbose=verbose,
        )
        if line:
            if prt:
                debug_print(line)
            else:
                lines.append(line)
    if not prt:
        return lines


def debug_line(callerframerecord, message=None, level=0, verbose=True):
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    if info.filename.startswith(settings.BASE_DIR):
        filename = info.filename[len(settings.BASE_DIR)+1:]
    else:
        return

    if info.function == '__call__':
        return

    if not message and not level:
        level = 3

    msg_list = []
    if level >= 3:
        msg_list.append(
            f"file={filename}" if verbose else f"{filename}"
        )
    if level >= 2:
        msg_list.append(
            f"func={info.function}" if verbose else f"{info.function}"
        )
    if level >= 1:
        msg_list.append(
            f"line={info.lineno}" if verbose else f"{info.lineno}"
        )
    if message:
        msg_list.append(message)

    return ';'.join(msg_list)


def debug_print(line):
    print(line)
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


def my_make_key_cache(*args):

    def add_value(values, value):
        if (value is None) \
                or isinstance(value, str) \
                or isinstance(value, datetime.date) \
                or is_number(value):
            values.append(value)

    values = []
    for value in args[1:]:
        if isinstance(value, str):
            add_value(values, value)
        else:
            try:
                for subvalue in iter(value):
                    add_value(values, subvalue)
            except TypeError:
                add_value(values, value)
    braces = ['{}'] * len(values)
    key = '|'.join(braces)
    key = key.format(*values)
    fo2logger.info(f'{args[0]}:{key}')
    key = hashlib.md5(key.encode('utf-8')).hexdigest()
    key = '_'.join([args[0], key])
    return key


def my_make_key_cache_slug(*args):
    return slugify(my_make_key_cache(*args))


def make_key_cache_OFF(ignore=[], obey=[]):
    stack1 = inspect.stack()[1]
    argvalues = inspect.getargvalues(stack1.frame).locals
    values = obey.copy()
    for key in argvalues:
        if key not in ignore:
            value = argvalues[key]
            if (value is None) \
                    or isinstance(value, str) \
                    or isinstance(value, datetime.date) \
                    or is_number(value):
                values.append(value)
    braces = ['{}'] * len(values)
    key = '|'.join([stack1.filename, *braces])
    key = key.format(*values)
    fo2logger.info(key[:200]+('...' if key[200:] else ''))
    key = hashlib.md5(key.encode('utf-8')).hexdigest()
    key = '_'.join([stack1.function, key])
    return key


def cache_ttl(cache, key):
    if _cache_local:
        exp_dt = cache._expire_info.get('FO2K:1:'+key)
        dt = datetime.datetime.fromtimestamp(exp_dt)
        now = datetime.datetime.now()
        ttl = dt - now
        seconds = ttl.seconds
    else:
        seconds = cache.ttl(key)
    fo2logger.info(f'cache expira em {seconds} segundos')
    return seconds


def untuple_keys(dicti):
    result = {}
    for key in dicti:
        if isinstance(key, tuple):
            for sub_key in key:
                result[sub_key] = dicti[key]
        else:
            result[key] = dicti[key]
    return result


def untuple_keys_concat(dicti, sep=""):

    def val_concat(key, master):
        if key in result:
            result[key] = sep.join([result[key], dicti[master]])
        else:
            result[key] = dicti[master]

    result = {}
    for key in dicti:
        if isinstance(key, tuple):
            for sub_key in key:
                val_concat(sub_key, key)
        else:
            val_concat(key, key)
    return result


def strdmy2date(text):
    return datetime.datetime.strptime(text, '%d/%m/%Y').date()


def ano_atual():
    hoje = datetime.date.today()
    return hoje.year


def mes_atual():
    hoje = datetime.date.today()
    return hoje.month


def dia_atual():
    hoje = datetime.date.today()
    return hoje.day


def acesso_externo():
    acesso_interno = AcessoInterno()
    try:
        acesso_externo = not acesso_interno.current_interno
    except Exception:
        acesso_externo = False
    return acesso_externo


def coalesce(value, default=None):
    """Recebendo valor, retorna este ou default"""
    if value is None:
        return default
    else:
        return value


def dict_coalesce(adict, fields, default):
    """Substitui None por default em fields de dicionário"""
    for field in fields:
        if adict[field] is None:
            adict[field] = default


def ldict_coalesce(adict, fields, default=None):
    """Substitui None por default em fields de lista de dicionários
    Caso default seja None, fields é uma lista de pares de fields e defaults.
    """
    for row in adict:
        if default is None:
            for fields_default in fields:
                dict_coalesce(row, *fields_default)
        else:
            dict_coalesce(row, fields, default)


def if_else(value, then_, else_):
    """Recebendo booleano, retorna then ou else"""
    if value:
        return then_
    else:
        return else_


def dict_if_else(adict, fields, then_, else_):
    """Substitui booleano por then ou else em fields de dicionário"""
    for field in fields:
        if adict[field]:
            adict[field] = then_
        else:
            adict[field] = else_


def ldict_if_else(adict, fields, then_=None, else_=None):
    """Substitui booleano por then ou else em fields de lista de dicionários
    Caso then seja None, fields é uma lista de trincas de fields, then e else.
    """
    for row in adict:
        if then_ is None:
            for fields_then_else in fields:
                dict_if_else(row, *fields_then_else)
        else:
            dict_if_else(row, fields, then_, else_)
