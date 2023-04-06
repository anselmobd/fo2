import datetime
from pprint import pprint


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


def ymd(data):
    """Return data in format YYYY-MM-DD"""
    return f"{data:%Y-%m-%d}"


def today_ymd():
    """Return today in format YYYY-MM-DD"""
    return ymd(datetime.date.today())


def yesterday():
    """Return yesterday"""
    return (
        datetime.date.today()
        - datetime.timedelta(days=1)
    )


def yesterday_ymd():
    """Return yesterday in format YYYY-MM-DD"""
    return ymd(yesterday())


def dmy(data):
    """Return data in format DD/MM/YYYY"""
    return f"{data:%d/%m/%Y}"


def dmy_or_empty(data):
    """Return dmy or empty"""
    return dmy(data) if data else ''
