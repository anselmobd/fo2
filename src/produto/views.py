from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
# from django.template.defaultfilters import lower
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def index(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          count(*) quant
        FROM BASI_030 p
        WHERE p.NIVEL_ESTRUTURA <> 0
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    row = data[0]
    context = {
        'quant': row['QUANT'],
    }
    return render(request, 'produto/index.html', context)


# ajax json example
def stat_nivel(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          p.NIVEL_ESTRUTURA nivel
        , count(*) quant
        FROM BASI_030 p
        WHERE p.NIVEL_ESTRUTURA <> 0
        GROUP BY
          p.NIVEL_ESTRUTURA
        ORDER BY
          p.NIVEL_ESTRUTURA
    '''
    cursor.execute(sql)
    data = cursor.fetchall()
    return JsonResponse(data, safe=False)


# ajax template example
def stat_nivelX(request):
    html = render_to_string('produto/ajax/desenvolvimento.html', {})
    return HttpResponse(html)


# ajax template, url with value
def stat_niveis(request, nivel):
    print(nivel)
    if nivel in ('1', '2', '9'):
        cursor = connections['so'].cursor()
        sql = '''
            SELECT
              p.REFERENCIA
            , p.DESCR_REFERENCIA
            FROM BASI_030 p
            WHERE p.NIVEL_ESTRUTURA = %s
            ORDER BY
              p.REFERENCIA
        '''
        cursor.execute(sql, [nivel])
        data = rows_to_dict_list(cursor)
        context = {
            'nivel': nivel,
            'headers': ('Referência', 'Descrição'),
            'fields': ('REFERENCIA', 'DESCR_REFERENCIA'),
            'data': data,
        }
        html = render_to_string('produto/ajax/stat_niveis.html', context)
        return HttpResponse(html)
    else:
        return stat_nivelX(request)
