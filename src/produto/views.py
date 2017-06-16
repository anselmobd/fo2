from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
# from django.template.defaultfilters import lower
from django.template.defaulttags import register

import produto.models  # import produtos_n1_pa_basic


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
            END ||
            CASE WHEN p.RESPONSAVEL IS NULL THEN ''
            ELSE '-' || p.RESPONSAVEL
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
            END ||
            CASE WHEN p.RESPONSAVEL IS NULL THEN ''
            ELSE '-' || p.RESPONSAVEL
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
    if nivel[0:4] in ('1-MD', '1-PA'):
        data = produto.models.produtos_n1_basic(nivel[2:])
        context = {
            'nivel': nivel,
            'headers': ('#', 'Referência', 'Descrição',
                        'Tamanhos', 'Cores', 'Estruturas', 'Roteiros'),
            'fields': ('ROWNUM', 'REFERENCIA', 'DESCR_REFERENCIA',
                       'TAMANHOS', 'CORES', 'ESTRUTURAS', 'ROTEIROS'),
            'data': data,
        }
        html = render_to_string('produto/ajax/stat_niveis.html', context)
        return HttpResponse(html)
    elif nivel in ('2', '9'):
        cursor = connections['so'].cursor()
        sql = '''
            SELECT
              ROWNUM
            , p.REFERENCIA
            , p.DESCR_REFERENCIA
            , ttt.TAMANHOS
            , ccc.CORES
            FROM BASI_030 p
            LEFT JOIN
              ( SELECT
                  tt.BASI030_NIVEL030
                , tt.BASI030_REFERENC
                , LISTAGG(tt.TAMANHO_REF, ', ')
                  WITHIN GROUP (ORDER BY tt.ORDEM_TAMANHO) tamanhos
              FROM
              ( SELECT DISTINCT
                  t.BASI030_NIVEL030
                , t.BASI030_REFERENC
                , t.TAMANHO_REF
                , tam.ORDEM_TAMANHO
                FROM basi_020 t
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = t.TAMANHO_REF
              )  tt
              GROUP BY
                tt.BASI030_NIVEL030
              , tt.BASI030_REFERENC
              ) ttt
            ON ttt.BASI030_NIVEL030 = p.NIVEL_ESTRUTURA
            AND ttt.BASI030_REFERENC = p.REFERENCIA
            LEFT JOIN
              ( SELECT
                  cc.NIVEL_ESTRUTURA
                , cc.GRUPO_ESTRUTURA
                , LISTAGG(cc.ITEM_ESTRUTURA, ', ')
                  WITHIN GROUP (ORDER BY cc.ITEM_ESTRUTURA) cores
              FROM
              ( SELECT DISTINCT
                  c.NIVEL_ESTRUTURA
                , c.GRUPO_ESTRUTURA
                , c.ITEM_ESTRUTURA
                FROM basi_010 c
              )  cc
              GROUP BY
                cc.NIVEL_ESTRUTURA
              , cc.GRUPO_ESTRUTURA
              ) ccc
             ON ccc.NIVEL_ESTRUTURA = p.NIVEL_ESTRUTURA
            AND ccc.GRUPO_ESTRUTURA = p.REFERENCIA
            WHERE p.NIVEL_ESTRUTURA = %s
            ORDER BY
              p.REFERENCIA
        '''
        cursor.execute(sql, [nivel[0]])
        data = rows_to_dict_list(cursor)
        context = {
            'nivel': nivel,
            'headers': ('#', 'Referência', 'Descrição', 'Tamanhos', 'Cores'),
            'fields': ('ROWNUM', 'REFERENCIA', 'DESCR_REFERENCIA',
                       'TAMANHOS', 'CORES'),
            'data': data,
        }
        html = render_to_string('produto/ajax/stat_niveis.html', context)
        return HttpResponse(html)
    else:
        return stat_nivelX(request)
