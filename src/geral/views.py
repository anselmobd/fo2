from django.shortcuts import render
from django.db import connections


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def index(request):
    context = {}
    return render(request, 'geral/index.html', context)


def deposito(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          d.CODIGO_DEPOSITO COD
        , d.DESCRICAO DESCR
        FROM BASI_205 d
        ORDER BY
          d.CODIGO_DEPOSITO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    context = {
        'headers': ('Depósito', 'Descrição'),
        'fields': ('COD', 'DESCR'),
        'data': data,
    }
    return render(request, 'geral/deposito.html', context)
