import datetime


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
