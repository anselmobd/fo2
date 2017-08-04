from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from fo2.template import group_rowspan

from .forms import LoteForm, ResponsPorEstagioForm, OpForm, OsForm
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
            link = ('OP')
            for row in data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa', 'Data/hora'),
                'o_fields': ('OP', 'SITU', 'PRG', 'DT'),
                'o_data': data,
                'o_link': link,
            })

        os_data = models.posicao_get_os(cursor, periodo, ordem_confeccao)
        if len(os_data) != 0:
            os_link = ('OS')
            for row in os_data:
                row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row['CNPJ9'],
                    row['CNPJ4'],
                    row['CNPJ2'])
                row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'os_headers': ('OS', 'Serviço', 'Terceiro',
                               'Emissão', 'Entrega',
                               'Situação', 'Cancelamento',
                               'Lotes', 'Quant.'),
                'os_fields': ('OS', 'SERV', 'TERC',
                              'DATA_EMISSAO', 'DATA_ENTREGA',
                              'SITUACAO', 'CANC',
                              'LOTES', 'QTD'),
                'os_data': os_data,
                'os_link': os_link,
            })

        data = models.posicao_get_item(cursor, periodo, ordem_confeccao)
        context.update({
            'i_headers': ('Quantidade', 'Tipo', 'Referência', 'Cor', 'Tamanho',
                          'Descrição', 'Item'),
            'i_fields': ('QTDE', 'TIPO', 'REF', 'COR', 'TAM',
                         'NARR', 'ITEM'),
            'i_data': data,
        })

        data = models.posicao_estagios(cursor, periodo, ordem_confeccao)
        group = ('EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A', 'Q_PERDA',
                 'FAMI', 'OS')
        group_rowspan(data, group)
        context.update({
            'e_headers': ('Estágio', 'Prog.', 'A Prod.',
                          'Em Prod.', 'Prod.', '2a.',
                          'Perda', 'Família', 'OS',
                          'Usuário', 'Data', 'Programa'),
            'e_fields': ('EST', 'Q_P', 'Q_AP',
                         'Q_EP', 'Q_PROD', 'Q_2A',
                         'Q_PERDA', 'FAMI', 'OS',
                         'USU', 'DT', 'PRG'),
            'e_group': group,
            'e_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

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


class Op(View):
    Form_class = OpForm
    template_name = 'lotes/op.html'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        data = models.op_lotes(cursor, op)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontrados',
            })
        else:
            link = ('LOTE')
            for row in data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
            context.update({
                'headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                            'Estágio', 'Período', 'OC', 'Quant.', 'Lote'),
                'fields': ('OS', 'REF', 'TAM', 'COR',
                           'EST', 'PERIODO', 'OC', 'QTD', 'LOTE'),
                'data': data,
                'link': link,
            })

            # informações gerais
            i_data = models.op_inform(cursor, op)
            row = i_data[0]
            if row['OP_REL'] == 0:
                row['OP_REL'] = ''
                i_link = []
            else:
                i_link = ('OP_RELAC')
                row['LINK'] = '/lotes/op/{}'.format(row['OP_REL'])
            context.update({
                'i_headers': ('Situação', 'Cancelamento',
                              'Tipo de OP', 'OP relacionada'),
                'i_fields': ('SITUACAO', 'CANCELAMENTO',
                             'TIPO_OP', 'OP_REL'),
                'i_data': i_data,
                'i_link': i_link,
            })
            context.update({
                'i2_headers': ('Tipo de referência', 'Referência',
                               'Alternativa', 'Roteiro',
                               'Qtd. Lotes', 'Quant. Itens'),
                'i2_fields': ('TIPO_REF', 'REF',
                              'ALTERNATIVA', 'ROTEIRO', 'LOTES', 'QTD'),
                'i2_data': i_data,
            })

            # Grade
            g_header, g_fields, g_data = models.op_sortimento(cursor, op)
            if len(g_data) != 0:
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                })

            # Estágios
            e_data = models.op_estagios(cursor, op)
            context.update({
                'e_headers': ('Estágio', '% Produzido', 'Itens Produzidos',
                              'Lotes no estágio'),
                'e_fields': ('EST', 'PERC', 'PROD', 'LOTES'),
                'e_data': e_data,
            })

            # Totais por referência + estágio
            t_data = models.op_ref_estagio(cursor, op)
            context.update({
                't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                              'Qtd. Lotes', 'Quant. Itens'),
                't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                't_data': t_data,
            })

            # OSs da OP
            os_data = models.op_get_os(cursor, op)
            if len(os_data) != 0:
                os_link = ('OS')
                for row in os_data:
                    row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
                context.update({
                    'os_headers': ('OS', 'Serviço', 'Terceiro',
                                   'Emissão', 'Entrega',
                                   'Situação', 'Cancelamento',
                                   'Lotes', 'Quant.'),
                    'os_fields': ('OS', 'SERV', 'TERC',
                                  'DATA_EMISSAO', 'DATA_ENTREGA',
                                  'SITUACAO', 'CANC',
                                  'LOTES', 'QTD'),
                    'os_data': os_data,
                    'os_link': os_link,
                })

            # Totais por OS + referência
            o_data = models.op_os_ref(cursor, op)
            o_link = ('OS')
            for row in o_data:
                if row['OS']:
                    row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                else:
                    row['LINK'] = None
            context.update({
                'o_headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                              'Qtd. Lotes', 'Quant. Itens'),
                'o_fields': ('OS', 'REF', 'TAM', 'COR', 'LOTES', 'QTD'),
                'o_data': o_data,
                'o_link': o_link,
            })
        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.Form_class(request.POST)
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connections['so'].cursor()
            context = self.mount_context(cursor, op)
        context['form'] = form
        return render(request, self.template_name, context)


class Os(View):
    Form_class = OsForm
    template_name = 'lotes/os.html'

    def mount_context(self, cursor, os):
        context = {'os': os}

        # A ser produzido
        data = models.os_inform(cursor, os)
        if len(data) == 0:
            context.update({
                'msg_erro': 'OS vazia',
            })
        else:
            for row in data:
                cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row['CNPJ9'],
                    row['CNPJ4'],
                    row['CNPJ2'])
                row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers': ('Serviço', 'Terceiro', 'Emissão', 'Entrega',
                            'Situação', 'Cancelamento'),
                'fields': ('SERV', 'TERC', 'DATA_EMISSAO', 'DATA_ENTREGA',
                           'SITUACAO', 'CANC'),
                'data': data,
            })
            context.update({
                'headers2': ('Observação', 'Lotes', 'Quant.'),
                'fields2': ('OBSERVACAO', 'LOTES', 'QTD'),
                'data2': data,
            })

            # Totais por OP
            o_data = models.os_op(cursor, os)
            if len(o_data) != 0:
                o_link = ('OP')
                for row in o_data:
                    row['LINK'] = '/lotes/op/{}'.format(row['OP'])
                context.update({
                    'o_headers': ('OP', 'Lotes', 'Quant.'),
                    'o_fields': ('OP', 'LOTES', 'QTD'),
                    'o_data': o_data,
                    'o_link': o_link,
                })

        # Grade
        g_header, g_fields, g_data = models.os_sortimento(cursor, os)
        if len(g_data) != 0:
            context.update({
                'g_headers': g_header,
                'g_fields': g_fields,
                'g_data': g_data,
            })

        # Itens para nota de OS
        i_data = models.os_itens(cursor, os)
        context.update({
            'i_headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Narrativa',
                          'Unidade', 'Valor unitário', 'Qtd.Estrutura',
                          'Qtd.Enviada', 'NF'),
            'i_fields': ('NIVEL', 'REF', 'COR', 'TAM', 'NARRATIVA',
                         'UN', 'VALOR_UN', 'QTD_ESTR', 'QTD_ENV', 'NF'),
            'i_data': i_data,
        })

        # Lotes ordenados por OS + referência + estágio
        l_data = models.os_lotes(cursor, os)
        if len(l_data) != 0:
            l_link = ('LOTE')
            for row in l_data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
            context.update({
                'l_headers': ('OP', 'Referência', 'Tamanho', 'Cor',
                              'Estágio', 'Período', 'OC', 'Quant.', 'Lote'),
                'l_fields': ('OP', 'REF', 'TAM', 'COR',
                             'EST', 'PERIODO', 'OC', 'QTD', 'LOTE'),
                'l_data': l_data,
                'l_link': l_link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'os' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.Form_class(request.POST)
        if 'os' in kwargs:
            form.data['os'] = kwargs['os']
        if form.is_valid():
            os = form.cleaned_data['os']
            cursor = connections['so'].cursor()
            context = self.mount_context(cursor, os)
        context['form'] = form
        return render(request, self.template_name, context)


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
