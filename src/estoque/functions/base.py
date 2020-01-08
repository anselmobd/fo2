import datetime
from pprint import pprint


def transfo2_num_doc(data, hora):
    if data is None:
        duration_secs = 0
    else:
        if hora is None:
            hora = datetime.time(0, 0)
        dt_inventario = datetime.datetime.combine(data, hora)
        origem_doc = datetime.datetime(2019, 11, 26, 23, 50)
        duration = dt_inventario - origem_doc
        duration_secs = duration.total_seconds()
    dez_minutos = int(duration_secs / 60 / 10)
    return '702{:06d}'.format(dez_minutos)


def transfo2_num_doc_dt(num_doc):
    origem_doc = datetime.datetime(2019, 11, 26, 23, 50)
    dez_minutos = int(str(num_doc)[3:])
    duration_secs = dez_minutos * 10 * 60
    dt_inventario = origem_doc + datetime.timedelta(0, duration_secs)
    return dt_inventario
