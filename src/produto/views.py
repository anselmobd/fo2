from django.shortcuts import render
from django.db import connections


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def index(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          count(*) quant
        FROM BASI_030
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    row = data[0]
    context = {
        'quant': row['QUANT'],
    }
    return render(request, 'produto/index.html', context)
