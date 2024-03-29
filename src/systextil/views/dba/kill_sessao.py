from pprint import pprint, pformat

from django.shortcuts import redirect

from fo2.connections import db_cursor_so

from utils.functions import fo2logger

from systextil.queries.dba.main import do_kill_sessao, get_info_sessao


def KillSessao(request, id_serial):
    cursor = db_cursor_so(request)
    
    fo2logger.info(f'KillSessao: id_serial: {id_serial}')
    sid = id_serial.split(',')[0]
    data = get_info_sessao(cursor, sid)
    info = pformat(data)
    fo2logger.info(f'KillSessao: info: {info}')

    if do_kill_sessao(cursor, id_serial):
        fo2logger.info(f'KillSessao: success')
    else:
        fo2logger.info(f'KillSessao: error')

    return redirect('systextil:travadora')
