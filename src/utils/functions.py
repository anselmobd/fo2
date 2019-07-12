import datetime
import inspect
import time
import logging
import inspect
import hashlib


logger = logging.getLogger('fo2')


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
    logger.info(key)
    key = hashlib.md5(key.encode('utf-8')).hexdigest()
    key = '_'.join([stack1.function, key])
    return key
