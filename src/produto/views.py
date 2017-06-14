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
          CASE WHEN p.NIVEL_ESTRUTURA = 1 THEN
            CASE WHEN p.REFERENCIA <= '99999' THEN '1-PA'
            ELSE '1-MD'
            END
          ELSE p.NIVEL_ESTRUTURA
          END nivel
        , count(*) quant
        FROM BASI_030 p
        WHERE p.NIVEL_ESTRUTURA <> 0
        GROUP BY
          CASE WHEN p.NIVEL_ESTRUTURA = 1 THEN
            CASE WHEN p.REFERENCIA <= '99999' THEN '1-PA'
            ELSE '1-MD'
            END
          ELSE p.NIVEL_ESTRUTURA
          END
        ORDER BY
          1
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
    if nivel in ('1-MD', '1-PA', '2', '9'):
        cursor = connections['so'].cursor()
        sql = '''
            SELECT
              p.REFERENCIA
            , p.DESCR_REFERENCIA
            , LISTAGG(t.TAMANHO_REF, ', ')
              WITHIN GROUP (ORDER BY tam.ORDEM_TAMANHO) TAMANHOS
            , cc.cores CORES
            FROM BASI_030 p
            JOIN basi_020 t
              ON t.BASI030_NIVEL030 = p.NIVEL_ESTRUTURA
             AND t.BASI030_REFERENC = p.REFERENCIA
            JOIN BASI_220 tam
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            JOIN
              ( SELECT
                  c.NIVEL_ESTRUTURA
                , c.GRUPO_ESTRUTURA
                , LISTAGG(c.ITEM_ESTRUTURA, ', ')
                  WITHIN GROUP (ORDER BY c.ITEM_ESTRUTURA) cores
                FROM
                  ( SELECT DISTINCT
                      i.NIVEL_ESTRUTURA
                    , i.GRUPO_ESTRUTURA
                    , i.ITEM_ESTRUTURA
                    FROM basi_010 i
                  )  c
                GROUP BY
                  c.NIVEL_ESTRUTURA
                , c.GRUPO_ESTRUTURA
              ) cc
              ON cc.NIVEL_ESTRUTURA = p.NIVEL_ESTRUTURA
             AND cc.GRUPO_ESTRUTURA = p.REFERENCIA
            WHERE p.NIVEL_ESTRUTURA = %s
        '''
        if nivel == '1-PA':
            sql = sql + '''
                AND p.REFERENCIA <= '99999'
            '''
        elif nivel == '1-MD':
            sql = sql + '''
                AND p.REFERENCIA > '99999'
            '''
        sql = sql + '''
            GROUP BY
              p.REFERENCIA
            , p.DESCR_REFERENCIA
            , cc.cores
            ORDER BY
              p.REFERENCIA
        '''
        cursor.execute(sql, [nivel[0]])
        data = rows_to_dict_list(cursor)
        context = {
            'nivel': nivel,
            'headers': ('Referência', 'Descrição', 'Tamanhos', 'Cores'),
            'fields': ('REFERENCIA', 'DESCR_REFERENCIA', 'TAMANHOS', 'CORES'),
            'data': data,
        }
        html = render_to_string('produto/ajax/stat_niveis.html', context)
        return HttpResponse(html)
    else:
        return stat_nivelX(request)
