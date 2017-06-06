from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse


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


def stat_nivel(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          p.NIVEL_ESTRUTURA nivel
        , count(*) quant
        FROM BASI_030 p
        GROUP BY
          p.NIVEL_ESTRUTURA
        ORDER BY
          p.NIVEL_ESTRUTURA
    '''
    cursor.execute(sql)
    data = cursor.fetchall()
    print(data)
    # data = {
    #     1: 123,
    #     2: 12,
    #     9: 1234,
    # }
    # return JsonResponse(data)
    return JsonResponse(data, safe=False)
