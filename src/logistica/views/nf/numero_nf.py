from pprint import pprint

from django.shortcuts import redirect

from fo2.connections import db_cursor_so

from logistica.queries import get_chave_pela_nf


def notafiscal_numero(request, *args, **kwargs):
    if 'nf' not in kwargs or kwargs['nf'] is None:
        return redirect('logistica:index')

    cursor = db_cursor_so(request)
    data_nf = get_chave_pela_nf(cursor, kwargs['nf'])
    if len(data_nf) == 0:
        return redirect('logistica:index')

    return redirect(
        'logistica:notafiscal_chave', data_nf[0]['NUMERO_DANF_NFE'])
