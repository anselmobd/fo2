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


def get_periodo_oc(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , TO_CHAR(p.DATA_INI_PERIODO, 'DD/MM/YYYY') INI
        , TO_CHAR(p.DATA_FIM_PERIODO - 1, 'DD/MM/YYYY') FIM
        , %s OC
        FROM PCPC_010 p
        WHERE AREA_PERIODO = 1
          AND PERIODO_PRODUCAO = %s
    '''
    cursor.execute(sql, [ordem_confeccao, periodo])
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        return False
    context.update({
        'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
        'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
        'l_data': data,
    })
    return True


def get_op(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.ORDEM_PRODUCAO OP
        , l.NOME_PROGRAMA_CRIACAO || ' - ' || p.DESCRICAO PRG
        , l.SITUACAO_ORDEM SITU
        , TO_CHAR(o.DATA_HORA, 'DD/MM/YYYY HH24:MI') DT
        FROM PCPC_040 l
        JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = l.NOME_PROGRAMA_CRIACAO
         AND p.LOCALE = 'pt_BR'
        LEFT JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
          AND rownum = 1
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        return False
    situacoes = {
        1: 'ORDEM CONF. GERADA',
        2: 'ORDENS EM PRODUCAO',
        9: 'ORDEM CANCELADA',
    }
    for row in data:
        if row['SITU'] in situacoes:
            row['SITU'] = '{} - {}'.format(row['SITU'], situacoes[row['SITU']])
    context.update({
        'o_headers': ('OP', 'Situação', 'Programa', 'Data/hora'),
        'o_fields': ('OP', 'SITU', 'PRG', 'DT'),
        'o_data': data,
    })
    return True


def get_item(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.PROCONF_NIVEL99
          || '.' || l.PROCONF_GRUPO
          || '.' || l.PROCONF_SUBGRUPO
          || '.' || l.PROCONF_ITEM ITEM
        , i.NARRATIVA NARR
        , l.QTDE_PROGRAMADA QTDE
        FROM PCPC_040 l
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND i.GRUPO_ESTRUTURA = l.PROCONF_GRUPO
         AND i.SUBGRU_ESTRUTURA = l.PROCONF_SUBGRUPO
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
    context.update({
        'i_headers': ('Item', 'Descrição', 'Quantidade'),
        'i_fields': ('ITEM', 'NARR', 'QTDE'),
        'i_data': data,
    })
    return True


def get_estagios(cursor, context, periodo, ordem_confeccao):
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.QTDE_PROGRAMADA Q_P
        , l.QTDE_EM_PRODUCAO_PACOTE Q_EP
        , l.QTDE_A_PRODUZIR_PACOTE Q_AP
        , l.CODIGO_FAMILIA FAMI
        , l.NUMERO_ORDEM OS
        , coalesce(d.USUARIO_SYSTEXTIL, ' ') USU
        , TO_CHAR(d.DATA_INSERCAO, 'DD/MM/YYYY HH24:MI') DT
        , coalesce(d.PROCESSO_SYSTEXTIL || ' - ' || p.DESCRICAO, ' ') PRG
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        LEFT JOIN PCPC_045 d
          ON d.PCPC040_PERCONF = l.PERIODO_PRODUCAO
         AND d.PCPC040_ORDCONF = l.ORDEM_CONFECCAO
         AND d.PCPC040_ESTCONF = l.CODIGO_ESTAGIO
        LEFT JOIN HDOC_036 p
          ON p.CODIGO_PROGRAMA = d.PROCESSO_SYSTEXTIL
         AND p.LOCALE = 'pt_BR'
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
        ORDER BY
          l.SEQ_OPERACAO
        , d.SEQUENCIA
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        return False
    for row in data:
        if row['DT'] is None:
            row['DT'] = ''
    context.update({
        'e_headers': ('Estágio', 'Prog.', 'Em Prod.',
                      'A Prod.', 'Família', 'Usuário', 'Data',
                      'Programa', 'OS'),
        'e_fields': ('EST', 'Q_P', 'Q_EP',
                     'Q_AP', 'FAMI', 'USU', 'DT', 'PRG', 'OS'),
        'e_data': data,
    })
    return True


def detalhes_lote(request, lote):
    periodo = lote[:4]
    ordem_confeccao = lote[-5:]
    cursor = connections['so'].cursor()
    context = {}

    if not get_periodo_oc(cursor, context, periodo, ordem_confeccao):
        return HttpResponse('')

    if not get_op(cursor, context, periodo, ordem_confeccao):
        return HttpResponse('')

    get_item(cursor, context, periodo, ordem_confeccao)

    get_estagios(cursor, context, periodo, ordem_confeccao)

    html = render_to_string('lotes/ajax/detalhes_lote.html', context)
    return HttpResponse(html)
