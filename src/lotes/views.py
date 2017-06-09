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


def get_op(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        FROM PCPC_040 l
        JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = l.NOME_PROGRAMA_CRIACAO
         AND p.LOCALE = 'pt_BR'
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        return False
    row = data[0]
    context.update({
        'o_headers': ('OP', 'Criada em'),
        'o_fields': ('OP', 'PRG'),
        'o_data': [{
            'OP': row['OP'],
            'PRG': row['PRG']
        }],
    })
    return True


def get_item(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , l.QTDE_PROGRAMADA QTDE
        , i.NARRATIVA NARR
        FROM PCPC_040 l
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND i.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND i.SUBGRU_ESTRUTURA = PROCONF_SUBGRUPO
         AND i.ITEM_ESTRUTURA = l.PROCONF_ITEM
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        return False
    row = data[0]
    context.update({
        'nivel': row['NIVEL'],
        'ref': row['REF'],
        'tam': row['TAM'],
        'cor': row['COR'],
        'qtde': row['QTDE'],
        'i_headers': ('Item', 'Descrição', 'Quantidade'),
        'i_fields': ('ITEM', 'NARR', 'QTD'),
        'i_data': [{
            'ITEM': '{}.{}.{}.{}'.format(
                row['NIVEL'], row['REF'], row['TAM'], row['COR']),
            'NARR': row['NARR'],
            'QTD': row['QTDE'],
        }],
    })
    return True


def detalhes_lote(request, lote):
    periodo = lote[:4]
    ordem_confeccao = lote[-5:]
    cursor = connections['so'].cursor()

    context = {
        'l_headers': ('Período', 'OC'),
        'l_fields': ('PER', 'OC'),
        'l_data': [{
            'PER': periodo,
            'OC': ordem_confeccao,
        }],
    }

    if not get_op(cursor, context, periodo, ordem_confeccao):
        return HttpResponse('')

    get_item(cursor, context, periodo, ordem_confeccao)

    html = render_to_string('lotes/ajax/detalhes_lote.html', context)
    return HttpResponse(html)
