import re
from pprint import pprint, pformat
import urllib

from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from fo2.models import rows_to_dict_list
from fo2.template import group_rowspan

from utils.forms import FiltroForm
from geral.views import dict_colecao_fluxos, get_roteiros_de_fluxo

from .forms import RefForm, ModeloForm, BuscaForm, GtinForm, \
    GeraRoteirosRefForm
import produto.queries as queries


def index(request):
    return render(request, 'produto/index.html')


def lista_item_n1_sem_preco_medio(request):
    context = {
        'titulo': 'Produto',
        'urltitulo': '/produto/',
        'subtitulo': 'Itens de nível 1 sem definição de preço médio',
    }
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          ptc.GRUPO_ESTRUTURA REF
        , ptc.SUBGRU_ESTRUTURA TAM
        , ptc.ITEM_ESTRUTURA COR
        FROM basi_010 ptc
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = ptc.SUBGRU_ESTRUTURA
        WHERE ptc.NIVEL_ESTRUTURA = 1
          AND (  ptc.PRECO_MEDIO IS NULL
              OR ptc.PRECO_MEDIO = 0
              )
        ORDER BY
          ptc.GRUPO_ESTRUTURA
        , tam.ORDEM_TAMANHO
        , ptc.ITEM_ESTRUTURA
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    if len(data) == 0:
        context.update({
            'mensagem':
                'Não há itens de nível 1 sem definição de preço médio.',
        })
    else:
        context.update({
            'headers': ('Referência', 'Tamanho', 'Cor'),
            'fields': ('REF', 'TAM', 'COR'),
            'data': data,
        })
    return render(request, 'layout/tabela_geral.html', context)


# UPDATE basi_010 ptc
# SET
#   ptc.PRECO_MEDIO = 2
# WHERE ptc.NIVEL_ESTRUTURA = 1
#   AND ptc.PRECO_MEDIO <> 2
# ;


def estatistica(request):
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
        'tela': 'Contagem e Listagem'
    }
    return render(request, 'produto/estatistica.html', context)


# ajax json example
def stat_nivel(request):
    cursor = connections['so'].cursor()

    # Marca com 'OP' produtos com alguma OP, porém sem nenhuma marca
    sql = '''
        UPDATE BASI_030 r
        SET
          r.RESPONSAVEL = 'OP'
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.RESPONSAVEL IS NULL
          AND EXISTS
        ( SELECT
            o.PERIODO_PRODUCAO
          FROM PCPC_040 o
          WHERE o.PROCONF_NIVEL99 = r.NIVEL_ESTRUTURA
            AND o.PROCONF_GRUPO = r.REFERENCIA
        )
    '''
    cursor.execute(sql)

    sql = '''
        SELECT
          CASE WHEN p.NIVEL_ESTRUTURA = 1 THEN
            CASE WHEN p.REFERENCIA <= '99999' THEN '1-PA'
            WHEN p.REFERENCIA like 'A%' THEN '1-PG'
            WHEN p.REFERENCIA like 'B%' THEN '1-PB'
            WHEN p.REFERENCIA like 'Z%' THEN '1-MP'
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
            WHEN p.REFERENCIA like 'A%' THEN '1-PG'
            WHEN p.REFERENCIA like 'B%' THEN '1-PB'
            WHEN p.REFERENCIA like 'Z%' THEN '1-MP'
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
    if nivel[0:4] in ('1-MD', '1-PB', '1-PG', '1-PA', '1-MP'):
        data = queries.produtos_n1_basic(nivel[2:])
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


class Ref(View):
    Form_class = RefForm
    template_name = 'produto/ref.html'
    title_name = 'Produto'

    def mount_context(self, cursor, ref):
        context = {'ref': ref}

        if len(ref) != 5:
            context.update({
                'msg_erro': 'Código de referência inválido',
            })
            return context

        # Informações básicas
        data = queries.ref_inform(cursor, ref)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Referência não encontrada',
            })
        else:
            modelo_link = \
                '<a href="{modelo_link}">{modelo}&nbsp;' \
                '<span class="glyphicon glyphicon-link" ' \
                'aria-hidden="true"></span></a>'.format(
                    modelo_link=reverse(
                        'produto:modelo__get', args=[data[0]['MODELO']]),
                    modelo=data[0]['MODELO'])
            if data[0]['MODELO'] != ' ':
                context.update({'modelo': modelo_link})
            context.update({
                'tipo': data[0]['TIPO'],
            })

            if data[0]['NUMERO_MOLDE'] is None:
                data[0]['NUMERO_MOLDE'] = '-'

            context.update({
                'headers': ('Descrição', 'Conta de estoque',
                            'Artigo', 'Linha', 'Coleção', 'Modelagem'),
                'fields': ('DESCR', 'CONTA_ESTOQUE',
                           'ARTIGO', 'LINHA', 'COLECAO', 'NUMERO_MOLDE'),
                'data': data,
            })

            for row in data:
                if row['COLECAO_CLIENTE'] is None:
                    row['COLECAO_CLIENTE'] = '-'
                if row['STATUS'] is None:
                    row['STATUS'] = '-'
                if row['CNPJ9'] is None:
                    row['CLIENTE'] = '-'
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers2': ('Coleção', 'Cliente', 'NCM',
                             'Status (Responsável)'),
                'fields2': ('COLECAO_CLIENTE', 'CLIENTE', 'NCM', 'STATUS'),
                'data2': data,
            })

            # PAs
            pa_data = queries.ref_utilizada_em(cursor, ref)
            pa_link = ('REF')
            for row in pa_data:
                if row['RESPONSAVEL'] is None:
                    row['RESPONSAVEL'] = '-'
                if row['REF'] != ' ':
                    row['LINK'] = reverse(
                        'produto:ref__get', args=[row['REF']])
            if len(pa_data) != 0:
                context.update({
                    'pa_headers': ('Tipo', 'Referência', 'Alternativa',
                                   'Responsável'),
                    'pa_fields': ('TIPO', 'REF', 'ALTERNATIVA', 'RESPONSAVEL'),
                    'pa_data': pa_data,
                    'pa_link': pa_link,
                })

            # Cores
            c_data = queries.ref_cores(cursor, ref)
            cores = ', '.join([data['COR'] for data in c_data])
            if len(c_data) != 0:
                context.update({
                    'c_headers': ('Cor', 'Descrição'),
                    'c_fields': ('COR', 'DESCR'),
                    'c_data': c_data,
                })

            # Tamanhos
            t_data = queries.ref_tamanhos(cursor, ref)
            if len(t_data) != 0:
                context.update({
                    't_headers': ('Tamanho', 'Descrição'),
                    't_fields': ('TAM', 'DESCR'),
                    't_data': t_data,
                })

            # Estruturas
            e_data = queries.ref_estruturas(cursor, ref)
            conta_ref = 0
            conta_tam_cor = 0
            for row in e_data:
                row['ALT'] = '{} ({})'.format(
                    row['ALTERNATIVA'], row['DESCR'])
                if row['TAM'] != '000' or row['COR'] != '000000':
                    conta_tam_cor += 1
                if row['REF'] != '-':
                    conta_ref += 1
                    row['REF'] = re.sub(
                        r'([A-Z0-9]+)',
                        r'<a href="'+reverse(
                            'produto:ref'
                        )+r'\1">\1&nbsp;<span '
                        'class="glyphicon glyphicon-link" '
                        'aria-hidden="true"></span></a>',
                        row['REF'])

            e_headers = ['Alternativa']
            e_fields = ['ALT']
            if conta_ref != 0:
                e_headers.append('Componente produto')
                e_fields.append('REF')
            if conta_tam_cor != 0:
                e_headers.extend(['Tamanho', 'Cor'])
                e_fields.extend(['TAM', 'COR'])

            if len(e_data) != 0:
                context.update({
                    'e_headers': e_headers,
                    'e_fields': e_fields,
                    'e_data': e_data,
                    'e_safe': ('REF',),
                })

            # Roteiros
            r_data = queries.ref_roteiros(cursor, ref)

            conta_tam_cor = 0
            for row in r_data:
                if row['TAM'] != '000' or row['COR'] != '000000':
                    conta_tam_cor += 1

            r_headers = ['Alternativa', 'Roteiro']
            r_fields = ['ALTERNATIVA', 'ROTEIRO']
            if conta_tam_cor != 0:
                r_headers.extend(['Tamanho', 'Cor'])
                r_fields.extend(['TAM', 'COR'])

            if len(r_data) != 0:
                context.update({
                    'r_headers': r_headers,
                    'r_fields': r_fields,
                    'r_data': r_data,
                })

            # Detalhando Roteiros
            roteiros = []
            for row in r_data:
                roteiro_tit = {
                    'alternativa': row['ALTERNATIVA'],
                    'roteiro': row['ROTEIRO'],
                    'tamanho': row['TAM'],
                    'cor': row['COR'],
                }
                roteiro = queries.ref_1roteiro(
                    cursor, ref, row['NUMERO_ALTERNATI'],
                    row['NUMERO_ROTEIRO'], row['TAM'], row['COR'])
                inserir = True
                for roteiro1 in roteiros:
                    if roteiro1['r_data'] == roteiro:
                        roteiro1['r_titulos'].append(roteiro_tit)
                        inserir = False
                if inserir:
                    roteiros.append({
                        'r_titulos': [roteiro_tit],
                        'r_headers': ['Sequência', 'Operação', 'Estágio',
                                      'Gargalo'],
                        'r_fields': ['SEQ', 'OPERACAO', 'ESTAGIO', 'GARGALO'],
                        'r_data': roteiro,
                    })
            context.update({
                'roteiros': roteiros,
            })

            estr_data = []
            for row in e_data:
                if not next((estr for estr in estr_data
                             if estr["ALTERNATIVA"] == row["ALTERNATIVA"]),
                            False):
                    estr_data.append(row)

            # Detalhando Estruturas
            estruts = []
            for row in estr_data:
                if row['ALTERNATIVA'] in \
                        [r['NUMERO_ALTERNATI'] for r in r_data]:
                    estrutura = queries.ref_estrutura_comp(
                        cursor, ref, row['ALTERNATIVA'])
                    e_link = ('REF')
                    dif_000000 = 0
                    for e_row in estrutura:
                        if e_row['COR_REF'] == cores:
                            e_row['COR_REF'] = '000000'
                        if e_row['COR_REF'] != '000000':
                            dif_000000 += 1
                        if e_row['NIVEL'] == '1':
                            e_row['REF|LINK'] = reverse(
                                'produto:ref__get', args=[e_row['REF']])
                        else:
                            e_row['REF|LINK'] = reverse(
                                'insumo:ref__get',
                                args=[e_row['NIVEL']+e_row['REF']])

                    e_headers = ['Sequência', 'Nível', 'Referência',
                                 'Descrição', 'Tamanho', 'Cor',
                                 'Alternativa', 'Consumo', 'Estágio']
                    e_fields = ['SEQUENCIA', 'NIVEL', 'REF',
                                'DESCR', 'TAM', 'COR',
                                'ALTERN', 'CONSUMO', 'ESTAGIO']
                    e_group = ['SEQUENCIA', 'NIVEL', 'REF', 'DESCR', 'TAM',
                               'ALTERN', 'CONSUMO', 'ESTAGIO']

                    if dif_000000 != 0:
                        e_headers.insert(0, 'Cor Alternativa')
                        e_fields.insert(0, 'COR_REF')
                        e_group.insert(0, 'COR_REF')

                    group_rowspan(estrutura, e_group)

                    estruts.append({
                        'alt': '{}-{}'.format(
                            row['ALTERNATIVA'], row['DESCR']),
                        'e_headers': e_headers,
                        'e_fields': e_fields,
                        'e_data': estrutura,
                        'e_link': e_link,
                        'e_group': e_group,
                    })

            context.update({
                'estruts': estruts,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'ref' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)


class Modelo(View):
    Form_class = ModeloForm
    template_name = 'produto/modelo.html'
    title_name = 'Modelo (parte numérica da referência do PA)'

    def mount_context(self, cursor, modelo):
        context = {'modelo': modelo}

        if len(modelo) not in (3, 4):
            context.update({
                'msg_erro': 'Modelo inválido',
            })
            return context

        # Informações básicas
        data = queries.modelo_inform(cursor, modelo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Modelo não encontrado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
                if row['CNPJ9'] == 0:
                    row['CLIENTE'] = ''
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers': ('Tipo', 'Referência', 'Coleção', 'Descrição',
                            'Cliente', 'Status (Responsável)'),
                'fields': ('TIPO', 'REF', 'COLECAO_CLIENTE', 'DESCR',
                           'CLIENTE', 'STATUS'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'modelo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'modelo' in kwargs:
            form.data['modelo'] = kwargs['modelo']
        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, modelo))
        context['form'] = form
        return render(request, self.template_name, context)


class Busca(View):
    Form_class = BuscaForm
    template_name = 'produto/busca.html'
    title_name = 'Listagem de produtos'

    def mount_context(self, cursor, busca, cor, roteiro, alternativa):
        context = {'busca': busca}

        if roteiro is None:
            roteiro = 0
        if alternativa is None:
            alternativa = 0
        data = queries.busca_produto(cursor, busca, cor, roteiro, alternativa)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum produto selecionado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
                if row['ALTERNATIVA'] is None:
                    row['ALTERNATIVA'] = '-'
                if row['ROTEIRO'] is None:
                    row['ROTEIRO'] = '-'
                if row['CNPJ9'] is None:
                    row['CNPJ9'] = 0
                if row['CNPJ4'] is None:
                    row['CNPJ4'] = 0
                if row['CNPJ2'] is None:
                    row['CNPJ2'] = 0
                if row['CNPJ9'] == 0:
                    row['CLIENTE'] = '-'
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['CLIENTE'])

            headers = ['#', 'Tipo', 'Referência', 'Descrição',
                       'Status (Responsável)', 'Cliente']
            fields = ['NUM', 'TIPO', 'REF', 'DESCR',
                      'RESP', 'CLIENTE']
            if len(cor) != 0:
                headers.append('Cor')
                headers.append('Cor Descr.')
                fields.append('COR')
                fields.append('COR_DESC')

            if roteiro != 0 or alternativa != 0:
                headers.append('Alternativa')
                fields.append('ALTERNATIVA')
                headers.append('Roteiro')
                fields.append('ROTEIRO')

            context.update({
                'headers': headers,
                'fields': fields,
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'busca' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'busca' in kwargs:
            form.data['busca'] = kwargs['busca']
        if form.is_valid():
            busca = form.cleaned_data['busca']
            cor = form.cleaned_data['cor']
            roteiro = form.cleaned_data['roteiro']
            alternativa = form.cleaned_data['alternativa']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, busca, cor, roteiro, alternativa))
        context['form'] = form
        return render(request, self.template_name, context)


class EstrEstagioDeInsumo(View):
    Form_class = FiltroForm
    template_name = 'produto/estr_estagio_de_insumo.html'
    title_name = 'Estágio de insumo'

    def mount_context(self, cursor):
        context = {}

        # Informações básicas
        data = queries.estr_estagio_de_insumo(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum erro de estágio de insumo encontrado.',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
            context.update({
                'headers': ('Ref.', 'Descrição', 'Tam.', 'Cor', 'Alt.',
                            'MP', 'MP Tam.', 'MP Cor', 'MP Alt.',
                            'Estágio não encontrado', 'Responsável'),
                'fields': ('REF', 'DESCR', 'TAM', 'COR', 'ALT',
                           'MP', 'MP_TAM', 'MP_COR', 'MP_ALT',
                           'ESTAGIO', 'RESPONSAVEL'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)


class Gtin(View):
    Form_class = GtinForm
    template_name = 'produto/gtin.html'
    title_name = 'GTIN (EAN13)'

    def mount_context(self, cursor, ref, gtin):
        context = {
            'ref': ref,
            'gtin': gtin,
            }

        data = queries.gtin(cursor, ref=ref, gtin=gtin)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            if row['GTIN'] == 'SEM GTIN':
                row['QTD'] = ''
            else:
                if row['QTD'] == 1:
                    row['QTD'] = 'Único'
                else:
                    row['QTD|LINK'] = '{}?{}'.format(
                        reverse('produto:gtin'),
                        urllib.parse.urlencode({
                            'gtin': row['GTIN'],
                        }))
        context.update({
            'headers': ('Referência', 'Cor', 'Tamanho', 'GTIN', 'Iguais'),
            'fields': ('REF', 'COR', 'TAM', 'GTIN', 'QTD'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'gtin' in request.GET:
            kwargs['gtin'] = request.GET['gtin']
            return self.post(request, *args, **kwargs)
        elif 'ref' in request.GET:
            kwargs['ref'] = request.GET['ref']
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if 'gtin' in kwargs:
            form.data['gtin'] = kwargs['gtin']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            gtin = form.cleaned_data['gtin']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref, gtin))
        context['form'] = form
        return render(request, self.template_name, context)


class RoteirosPadraoRef(View):
    Form_class = GeraRoteirosRefForm
    template_name = 'produto/roteiros_padrao_ref.html'
    title_name = 'Roteiros padrão por referência'

    def mount_context(self, cursor, ref):
        context = {
            'ref': ref,
            }

        data = queries.ref_inform(cursor, ref)
        if len(data) == 0:
            context.update({'erro': 'Referência não encontrada'})
            return context

        info = data[0]
        tipo = info['TIPO'].lower()
        colecao = info['COLECAO']
        colecao_id = info['CODIGO_COLECAO']

        fluxos = dict_colecao_fluxos(colecao_id, tipo, ref)

        roteiros = []
        for fluxo in fluxos:
            fluxo_roteiros = get_roteiros_de_fluxo(fluxo)
            if tipo in fluxo_roteiros:
                roteiros += list(fluxo_roteiros[tipo].keys())

        estagios = {}
        for fluxo in fluxos:
            fluxo_roteiros = get_roteiros_de_fluxo(fluxo)
            if tipo in fluxo_roteiros:
                for rot_num in fluxo_roteiros[tipo]:
                    estagios_os = fluxo_roteiros[tipo][rot_num][0]
                    gargalo = fluxo_roteiros[tipo][rot_num][1]
                    estagios_a_criar = []
                    for estagio in estagios_os:
                        if isinstance(estagio, int):
                            if estagio == gargalo:
                                estagios_a_criar.append((estagio, 'Gargalo'))
                            else:
                                estagios_a_criar.append((estagio,))
                    estagios.update({
                        rot_num: estagios_a_criar
                    })

        context.update({
            'colecao': colecao,
            'tipo': tipo,
            'fluxos': fluxos,
            'roteiros': roteiros,
            'estagios': estagios,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'ref' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs and kwargs['ref'] is not None:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)


def gera_roteiros_padrao_ref(ref):
    cursor = connections['so'].cursor()
    data = queries.ref_inform(cursor, ref)

    info = data[0]
    tipo = info['TIPO'].lower()
    colecao = info['COLECAO']
    colecao_id = info['CODIGO_COLECAO']

    fluxos = dict_colecao_fluxos(colecao_id, tipo, ref)

    roteiros = {}
    for fluxo in fluxos:
        fluxo_roteiros = get_roteiros_de_fluxo(fluxo)
        if tipo in fluxo_roteiros:
            for rot_num in fluxo_roteiros[tipo]:
                roteiros.update({
                    rot_num: fluxo_roteiros[tipo][rot_num]
                })

    roteiros_db = queries.get_roteiros_ref(cursor, ref)

    output = ''
    sqls = []
    for roteiro in roteiros:
        roteiros[roteiro][0] = [
            est for est in roteiros[roteiro][0] if isinstance(est, int)]
        estagios = roteiros[roteiro][0]
        gargalo = roteiros[roteiro][1]
        output += '\nroteiro {}\n'.format(roteiro)
        output += 'padrao: '+pformat(roteiros[roteiro], indent=4)+'\n'

        tam_cores = set()
        for row in roteiros_db:
            if row['NUMERO_ROTEIRO'] == roteiro:
                tam_cores.add(
                    (row['SUBGRU_ESTRUTURA'], row['ITEM_ESTRUTURA']))

        if len(tam_cores) == 0:
                tam_cores.add(('000', '000000'))

        for tam_cor in tam_cores:
            output += 'tamanho, cor: '+pformat(tam_cor, indent=4)+'\n'

            tam, cor = tam_cor
            estagios_db = [[], None]
            for row in roteiros_db:
                if row['NUMERO_ROTEIRO'] == roteiro and \
                        row['SUBGRU_ESTRUTURA'] == tam and \
                        row['ITEM_ESTRUTURA'] == cor:
                    estagios_db[0].append(row['CODIGO_ESTAGIO'])
                    if row['IND_ESTAGIO_GARGALO'] == 1:
                        if estagios_db[1] is None:
                            estagios_db[1] = row['CODIGO_ESTAGIO']
                        else:
                            estagios_db[1] = 999

            output += 'systextil: '+pformat(estagios_db, indent=4)+'\n'
            if estagios_db != roteiros[roteiro]:
                if estagios_db[0] != estagios:
                    if len(estagios_db[0]) != 0:
                        output += '-> exclui estagios\n'
                        delete = queries.mount_delete_estagios(
                            roteiro, ref, tam, cor)
                        # print(delete)
                        sqls.append(delete)
                    output += '-> inclui estagios\n'
                    inserts = queries.mount_inserts_estagios(
                        roteiro, ref, tam, cor, estagios)
                    for insert in inserts:
                        # print(insert)
                        sqls.append(insert)
                else:
                    if estagios_db[1] is not None:
                        output += '-> exclui gargalo {}\n'.format(
                            estagios_db[1])
                        unsetg = queries.mount_unset_gargalo(
                            roteiro, ref, tam, cor)
                        # print(unsetg)
                        sqls.append(unsetg)
                output += '-> inclui gargalo {}\n'.format(gargalo)
                setg = queries.mount_set_gargalo(
                    roteiro, ref, tam, cor, gargalo)
                # print(setg)
                sqls.append(setg)

    # output += pformat(sqls, indent=4)+'\n'
    for sql in sqls:
        # print(sql)
        cursor.execute(sql)

    return output


class GeraRoteirosPadraoRef(View):

    def get(self, request, *args, **kwargs):
        ref = kwargs['ref']
        nada = HttpResponse('', content_type='text/plain')
        if ref is None:
            return nada

        ref = ref.upper()
        cursor = connections['so'].cursor()
        data = queries.ref_inform(cursor, ref)
        if len(data) == 0:
            return nada

        output = gera_roteiros_padrao_ref(ref)

        return HttpResponse(
            output,
            content_type='text/plain')
