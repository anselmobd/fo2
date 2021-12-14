from pprint import pprint

from django.shortcuts import redirect

from fo2.connections import db_cursor_so

from systextil.queries.dba.main import do_kill_sessao


def KillSessao(request, id_serial):
    cursor = db_cursor_so(request)
    do_kill_sessao(cursor, id_serial)
    return redirect('systextil:travadora')
