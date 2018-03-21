import datetime
# from pprint import pprint


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
    # print('IN min_not_None')
    # pprint(args)
    mini = None
    for v in args:
        # pprint(v)
        if v:
            # print('v not None')
            if mini:
                # print('mini not None')
                mini = min(
                    mini,
                    v)
            else:
                mini = v
            # print('mini = {}'.format(mini))
    # print('OUT min_not_None')
    return mini
