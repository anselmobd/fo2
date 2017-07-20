from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from fo2.template import group_rowspan

from .forms import LoteForm, ResponsPorEstagioForm, OpForm
import lotes.models as models


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def index(request):
    context = {}
    return render(request, 'lotes/index.html', context)


class Posicao(View):
    Form_class = LoteForm
    template_name = 'lotes/posicao.html'

    def mount_context(self, cursor, periodo, ordem_confeccao):
        context = {}

        data = models.posicao_lote(cursor, periodo, ordem_confeccao)
        row = data[0]
        context.update({
            'codigo_estagio': row['CODIGO_ESTAGIO'],
            'descricao_estagio': row['DESCRICAO_ESTAGIO'],
        })

        data = models.posicao_periodo_oc(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
                'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
                'l_data': data,
            })

        data = models.posicao_get_op(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa', 'Data/hora'),
                'o_fields': ('OP', 'SITU', 'PRG', 'DT'),
                'o_data': data,
            })

        data = models.posicao_get_item(cursor, periodo, ordem_confeccao)
        context.update({
            'i_headers': ('Item', 'Descrição', 'Quantidade'),
            'i_fields': ('ITEM', 'NARR', 'QTDE'),
            'i_data': data,
        })

        data = models.posicao_estagios(cursor, periodo, ordem_confeccao)
        group = ('EST', 'Q_P', 'Q_EP', 'Q_AP', 'FAMI', 'OS')
        group_rowspan(data, group)
        context.update({
            'e_headers': ('Estágio', 'Prog.', 'Em Prod.',
                          'A Prod.', 'Família', 'OS',
                          'Usuário', 'Data', 'Programa'),
            'e_fields': ('EST', 'Q_P', 'Q_EP',
                         'Q_AP', 'FAMI', 'OS',
                         'USU', 'DT', 'PRG'),
            'e_group': group,
            'e_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' not in kwargs:
            form = self.Form_class()
            context = {
                'form': form
            }
            return render(request, self.template_name, context)
        else:
            return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]

            cursor = connections['so'].cursor()
            data = models.existe_lote(cursor, periodo, ordem_confeccao)
            if len(data) == 0:
                context['erro'] = '.'
            else:
                context['lote'] = lote
                data = self.mount_context(cursor, periodo, ordem_confeccao)
                context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


def op(request):
    context = {}
    if request.method == 'POST':
        form = OpForm(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            context.update({
                'op': op,
            })
            cursor = connections['so'].cursor()

            # Lotes ordenados por OS + referência + estágio
            sql = '''
                SELECT
                  CASE WHEN dos.NUMERO_ORDEM IS NULL
                  THEN '0'
                  ELSE l.NUMERO_ORDEM || ' (' || eos.DESCRICAO || ')'
                  END OS
                , l.PROCONF_GRUPO REF
                , l.PROCONF_SUBGRUPO TAM
                , l.PROCONF_ITEM COR
                , COALESCE(
                  ( SELECT
                      le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO
                    FROM PCPC_040 le
                    JOIN MQOP_005 ed
                      ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
                    WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                      AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                      AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                  )
                  , 'FINALIZADO'
                  ) EST
                , l.PERIODO_PRODUCAO PERIODO
                , l.ORDEM_CONFECCAO OC
                , l.QTDE_PROGRAMADA QTD
                FROM (
                  SELECT
                    os.PERIODO_PRODUCAO
                  , os.ORDEM_CONFECCAO
                  , os.PROCONF_GRUPO
                  , os.PROCONF_SUBGRUPO
                  , os.PROCONF_ITEM
                  , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
                  , max( os.QTDE_PROGRAMADA ) QTDE_PROGRAMADA
                  FROM PCPC_040 os
                  WHERE os.ORDEM_PRODUCAO = %s
                  GROUP BY
                    os.PERIODO_PRODUCAO
                  , os.ORDEM_CONFECCAO
                  , os.PROCONF_GRUPO
                  , os.PROCONF_SUBGRUPO
                  , os.PROCONF_ITEM
                ) l
                LEFT JOIN PCPC_040 dos
                  ON l.NUMERO_ORDEM <> 0
                 AND dos.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                 AND dos.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                 AND dos.NUMERO_ORDEM = l.NUMERO_ORDEM
                LEFT JOIN MQOP_005 eos
                  ON eos.CODIGO_ESTAGIO = dos.CODIGO_ESTAGIO
                LEFT JOIN BASI_220 t
                  ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
                ORDER BY
                  l.NUMERO_ORDEM
                , l.PROCONF_GRUPO
                , l.PROCONF_ITEM
                , t.ORDEM_TAMANHO
                , l.PERIODO_PRODUCAO
                , l.ORDEM_CONFECCAO
            '''
            cursor.execute(sql, (op,))
            data = rows_to_dict_list(cursor)
            if len(data) == 0:
                context.update({
                    'msg_erro': 'Lotes não encontrados',
                })
            else:
                context.update({
                    'headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                                'Estágio', 'Período', 'OC', 'Quant.'),
                    'fields': ('OS', 'REF', 'TAM', 'COR',
                               'EST', 'PERIODO', 'OC', 'QTD'),
                    'data': data,
                })

                # Totais por referência + estágio
                sql = '''
                    SELECT
                      lote.REF
                    , lote.TAM
                    , lote.COR
                    , lote.EST
                    , count(*) LOTES
                    , sum(lote.QTD) QTD
                    FROM (
                      SELECT
                        l.PROCONF_GRUPO REF
                      , l.PROCONF_SUBGRUPO TAM
                      , l.PROCONF_ITEM COR
                      , COALESCE(
                          ( SELECT
                              le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO
                            FROM PCPC_040 le
                            JOIN MQOP_005 ed
                              ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
                            WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                              AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                              AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                          )
                        , 'FINALIZADO'
                        ) EST
                      , l.QTDE_PROGRAMADA QTD
                      FROM (
                        SELECT
                          os.PROCONF_GRUPO
                        , os.PROCONF_SUBGRUPO
                        , os.PROCONF_ITEM
                        , os.PERIODO_PRODUCAO
                        , os.ORDEM_CONFECCAO
                        , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
                        , max( os.QTDE_PROGRAMADA ) QTDE_PROGRAMADA
                        FROM PCPC_040 os
                        WHERE os.ORDEM_PRODUCAO = %s
                        GROUP BY
                          os.PROCONF_GRUPO
                        , os.PROCONF_SUBGRUPO
                        , os.PROCONF_ITEM
                        , os.PERIODO_PRODUCAO
                        , os.ORDEM_CONFECCAO
                      ) l
                    ) lote
                    LEFT JOIN BASI_220 t
                      ON t.TAMANHO_REF = lote.TAM
                    GROUP BY
                      lote.REF
                    , lote.COR
                    , t.ORDEM_TAMANHO
                    , lote.TAM
                    , lote.EST
                    ORDER BY
                      lote.REF
                    , lote.COR
                    , t.ORDEM_TAMANHO
                    , lote.EST
                '''
                cursor.execute(sql, (op,))
                t_data = rows_to_dict_list(cursor)
                context.update({
                    't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                                  'Qtd. Lotes', 'Quant. Itens'),
                    't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                    't_data': t_data,
                })

                # Totais por OS + referência
                sql = """
                    SELECT
                      l.NUMERO_ORDEM OS
                    , l.PROCONF_GRUPO REF
                    , l.PROCONF_SUBGRUPO TAM
                    , l.PROCONF_ITEM COR
                    , count( l.ORDEM_CONFECCAO ) LOTES
                    , SUM (
                        ( SELECT
                            q.QTDE_PROGRAMADA
                          FROM PCPC_040 q
                          WHERE q.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                            AND q.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                            AND q.SEQ_OPERACAO = (
                              SELECT
                                min(o.SEQ_OPERACAO)
                              FROM PCPC_040 o
                              WHERE o.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                                AND o.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                            )
                        )
                      ) QTD
                    FROM (
                      SELECT DISTINCT
                        os.ORDEM_PRODUCAO
                      , os.PERIODO_PRODUCAO
                      , os.ORDEM_CONFECCAO
                      , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
                      , os.PROCONF_GRUPO
                      , os.PROCONF_SUBGRUPO
                      , os.PROCONF_ITEM
                      FROM PCPC_040 os
                      WHERE os.ORDEM_PRODUCAO = %s
                      GROUP BY
                        os.ORDEM_PRODUCAO
                      , os.PERIODO_PRODUCAO
                      , os.ORDEM_CONFECCAO
                      , os.PROCONF_GRUPO
                      , os.PROCONF_SUBGRUPO
                      , os.PROCONF_ITEM
                    ) l
                    LEFT JOIN BASI_220 t
                      ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
                    GROUP BY
                      l.ORDEM_PRODUCAO
                    , l.NUMERO_ORDEM
                    , l.PROCONF_GRUPO
                    , l.PROCONF_SUBGRUPO
                    , t.ORDEM_TAMANHO
                    , l.PROCONF_ITEM
                    ORDER BY
                      l.ORDEM_PRODUCAO
                    , l.NUMERO_ORDEM
                    , l.PROCONF_GRUPO
                    , l.PROCONF_ITEM
                    , t.ORDEM_TAMANHO
                """
                cursor.execute(sql, (op,))
                o_data = rows_to_dict_list(cursor)
                context.update({
                    'o_headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                                  'Qtd. Lotes', 'Quant. Itens'),
                    'o_fields': ('OS', 'REF', 'TAM', 'COR', 'LOTES', 'QTD'),
                    'o_data': o_data,
                })

    else:
        form = OpForm()

    context['form'] = form
    return render(request, 'lotes/op.html', context)


def respons(request):
    context = {}
    if request.method == 'POST':
        form = ResponsPorEstagioForm(request.POST)
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            usuario = '%'+form.cleaned_data['usuario']+'%'
            ordem = form.cleaned_data['ordem']
            cursor = connections['so'].cursor()
            sql = """
                SELECT
                  e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
                , CASE WHEN u.USUARIO IS NULL
                  THEN '--SEM RESPONSAVEL--'
                  ELSE u.USUARIO || ' (' || u.CODIGO_USUARIO || ')'
                  END USUARIO
                FROM MQOP_005 e
                LEFT JOIN MQOP_006 r
                  ON r.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
                 AND r.TIPO_MOVIMENTO = 0
                LEFT JOIN HDOC_030 u
                  ON u.CODIGO_USUARIO = r.CODIGO_USUARIO
                WHERE e.CODIGO_ESTAGIO <> 0
                  AND ( %s is NULL OR e.CODIGO_ESTAGIO = %s )
                  AND ( coalesce( u.USUARIO, '_' ) like %s )
                ORDER BY
            """
            if ordem == 'e':
                sql = sql + '''
                      e.CODIGO_ESTAGIO
                    , u.USUARIO
                '''
            else:
                sql = sql + '''
                      u.USUARIO
                    , e.CODIGO_ESTAGIO
                '''
            cursor.execute(sql, (estagio, estagio, usuario))
            data = rows_to_dict_list(cursor)
            if len(data) != 0:
                if ordem == 'e':
                    context = {
                        'headers': ('Estágio', 'Usuário'),
                        'fields': ('ESTAGIO', 'USUARIO'),
                        'data': data,
                    }
                else:
                    context = {
                        'headers': ('Usuário', 'Estágio'),
                        'fields': ('USUARIO', 'ESTAGIO'),
                        'data': data,
                    }
    else:
        form = ResponsPorEstagioForm()
    context['form'] = form
    return render(request, 'lotes/respons.html', context)


# OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD


def posicaoOri(request):
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
                  CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE = 0 THEN 0
                  ELSE l.CODIGO_ESTAGIO
                  END CODIGO_ESTAGIO
                , CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE = 0 THEN 'FINALIZADO'
                  ELSE e.DESCRICAO
                  END DESCRICAO_ESTAGIO
                FROM PCPC_040 l
                JOIN MQOP_005 e
                  ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
                WHERE l.PERIODO_PRODUCAO = %s
                  AND l.ORDEM_CONFECCAO = %s
                  AND l.SEQ_OPERACAO =
                  (
                    SELECT
                      max(lms.SEQ_OPERACAO)
                    FROM PCPC_040 lms
                    WHERE lms.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND lms.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                      AND lms.QTDE_EM_PRODUCAO_PACOTE =
                          lms.QTDE_A_PRODUZIR_PACOTE
                  )
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
    return render(request, 'lotes/posicaoOri.html', context)


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
