from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse
from django.template.loader import render_to_string

from .forms import LoteForm


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def index(request):
    context = {}
    return render(request, 'lotes/index.html', context)


def posicao(request):
    context = {}
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]
            cursor = connections['so'].cursor()
            sql = '''
                SELECT
                  l.CODIGO_ESTAGIO
                , e.DESCRICAO DESCRICAO_ESTAGIO
                , l.QTDE_EM_PRODUCAO_PACOTE
                FROM PCPC_040 l
                JOIN MQOP_005 e
                  ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
                WHERE l.PERIODO_PRODUCAO = %s
                  AND l.ORDEM_CONFECCAO = %s
                  AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            '''
            cursor.execute(sql, [periodo, ordem_confeccao])
            data = rows_to_dict_list(cursor)
            if len(data) == 0:
                context = {
                    'lote': lote,
                    'codigo_estagio': 'X',
                    'descricao_estagio': 'LOTE NÃO ENCONTRADO',
                }
            else:
                row = data[0]
                context = {
                    'lote': lote,
                    'codigo_estagio': row['CODIGO_ESTAGIO'],
                    'descricao_estagio': row['DESCRICAO_ESTAGIO'],
                }
    else:
        form = LoteForm()
    context['form'] = form
    return render(request, 'lotes/posicao.html', context)


def get_item(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , l.QTDE_PROGRAMADA QTDE
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    return data


def get_op(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    return data


def detalhes_lote(request, lote):
    periodo = lote[:4]
    ordem_confeccao = lote[-5:]
    cursor = connections['so'].cursor()

    context = {}

    data = get_op(cursor, periodo, ordem_confeccao)
    if len(data) == 0:
        return HttpResponse('')

    row = data[0]
    context.update({
        'op': row['OP'],
        'periodo': periodo,
        'ordem_confeccao': ordem_confeccao,
        'o_headers': ('OP', 'Período', 'OC'),
        'o_fields': ('OP', 'PER', 'OC'),
        'o_data': [{
            'OP': row['OP'],
            'PER': periodo,
            'OC': ordem_confeccao,
        }],
    })

    data = get_item(cursor, periodo, ordem_confeccao)
    row = data[0]
    context.update({
        'nivel': row['NIVEL'],
        'ref': row['REF'],
        'tam': row['TAM'],
        'cor': row['COR'],
        'qtde': row['QTDE'],
        'i_headers': ('Item', 'Quantidade'),
        'i_fields': ('ITEM', 'QTD'),
        'i_data': [{
            'ITEM': '{}.{}.{}.{}'.format(
                row['NIVEL'], row['REF'], row['TAM'], row['COR']),
            'QTD': row['QTDE'],
        }],
    })

    html = render_to_string('lotes/ajax/detalhes_lote.html', context)
    return HttpResponse(html)
