from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from fo2.models import rows_to_dict_list

from .forms import RefForm, ModeloForm
from utils.forms import FiltroForm
import produto.models as models


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
            WHEN p.REFERENCIA like 'A%' or p.REFERENCIA like 'B%' THEN '1-PG'
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
            WHEN p.REFERENCIA like 'A%' or p.REFERENCIA like 'B%' THEN '1-PG'
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
    if nivel[0:4] in ('1-MD', '1-PG', '1-PA', '1-MP'):
        data = models.produtos_n1_basic(nivel[2:])
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
    title_name = 'Produtos confeccionados'

    def mount_context(self, cursor, ref):
        context = {'ref': ref}

        if len(ref) != 5:
            context.update({
                'msg_erro': 'Código de referência inválido',
            })
            return context

        # Informações básicas
        data = models.ref_inform(cursor, ref)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Referência não encontrada',
            })
        else:
            modelo_link = \
                '<a href="/produto/modelo/{}">{}&nbsp;' \
                '<span class="glyphicon glyphicon-link" ' \
                'aria-hidden="true"></span></a>'.format(
                    data[0]['MODELO'], data[0]['MODELO'])
            if data[0]['MODELO'] != ' ':
                context.update({'modelo': modelo_link})
            context.update({
                'tipo': data[0]['TIPO'],
            })

            context.update({
                'headers': ('Descrição', 'Conta de estoque',
                            'Artigo', 'Linha', 'Coleção'),
                'fields': ('DESCR', 'CONTA_ESTOQUE',
                           'ARTIGO', 'LINHA', 'COLECAO'),
                'data': data,
            })

            for row in data:
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
            pa_data = models.ref_utilizada_em(cursor, ref)
            pa_link = ('REF')
            for row in pa_data:
                if row['REF'] != ' ':
                    row['LINK'] = '/produto/ref/{}'.format(row['REF'])
            if len(pa_data) != 0:
                context.update({
                    'pa_headers': ('Tipo', 'Referência', 'Alternativa'),
                    'pa_fields': ('TIPO', 'REF', 'ALTERNATIVA'),
                    'pa_data': pa_data,
                    'pa_link': pa_link,
                })

            # Cores
            c_data = models.ref_cores(cursor, ref)
            cores = ', '.join([data['COR'] for data in c_data])
            if len(c_data) != 0:
                context.update({
                    'c_headers': ('Cor', 'Descrição'),
                    'c_fields': ('COR', 'DESCR'),
                    'c_data': c_data,
                })

            # Tamanhos
            t_data = models.ref_tamanhos(cursor, ref)
            if len(t_data) != 0:
                context.update({
                    't_headers': ('Tamanho', 'Descrição'),
                    't_fields': ('TAM', 'DESCR'),
                    't_data': t_data,
                })

            # Estruturas
            e_data = models.ref_estruturas(cursor, ref)
            e_link = ('REF')
            for row in e_data:
                if row['REF'] != ' ':
                    row['LINK'] = '/produto/ref/{}'.format(row['REF'])
            if len(e_data) != 0:
                context.update({
                    'e_headers': ('Alternativa', 'Descrição',
                                  'Componente produto'),
                    'e_fields': ('ALTERNATIVA', 'DESCR', 'REF'),
                    'e_data': e_data,
                    'e_link': e_link,
                })

            # Roteiros
            r_data = models.ref_roteiros(cursor, ref)
            if len(r_data) != 0:
                context.update({
                    'r_headers': ('Alternativa', 'Roteiro'),
                    'r_fields': ('ALTERNATIVA', 'ROTEIRO'),
                    'r_data': r_data,
                })

            # Detalhando Roteiros
            roteiros = []
            for row in r_data:
                roteiro = models.ref_1roteiro(
                    cursor, ref, row['NUMERO_ALTERNATI'],
                    row['NUMERO_ROTEIRO'])
                roteiros.append({
                    'alternativa': row['ALTERNATIVA'],
                    'roteiro': row['ROTEIRO'],
                    'r_headers': ['Sequência', 'Operação', 'Estágio',
                                  'Gargalo'],
                    'r_fields': ['SEQ', 'OPERACAO', 'ESTAGIO', 'GARGALO'],
                    'r_data': roteiro,
                })
            context.update({
                'roteiros': roteiros,
            })

            # Detalhando Estruturas
            estruts = []
            for row in e_data:
                if row['ALTERNATIVA'] in \
                        [r['NUMERO_ALTERNATI'] for r in r_data]:
                    estrutura = models.ref_estrutura_comp(
                        cursor, ref, row['ALTERNATIVA'])
                    e_link = ('REF')
                    dif_000000 = 0
                    for e_row in estrutura:
                        if e_row['COR_REF'] == cores:
                            e_row['COR_REF'] = '000000'
                        if e_row['COR_REF'] != '000000':
                            dif_000000 += 1
                        if e_row['NIVEL'] == '1':
                            e_row['LINK'] = '/produto/ref/{}'.format(
                                e_row['REF'])
                        else:
                            e_row['LINK'] = '/insumo/ref/{}{}'.format(
                                e_row['NIVEL'], e_row['REF'])
                    estruts.append({
                        'alt': '{}-{}'.format(
                            row['ALTERNATIVA'], row['DESCR']),
                        'e_headers': ['Sequência', 'Nível', 'Referência',
                                      'Descrição', 'Tamanho', 'Cor',
                                      'Alternativa', 'Consumo', 'Estágio'],
                        'e_fields': ['SEQUENCIA', 'NIVEL', 'REF',
                                     'DESCR', 'TAM', 'COR',
                                     'ALTERN', 'CONSUMO', 'ESTAGIO'],
                        'e_data': estrutura,
                        'e_link': e_link,
                    })
                    if dif_000000 != 0:
                        estruts[-1]['e_headers'].insert(0, 'Cor Referência')
                        estruts[-1]['e_fields'].insert(0, 'COR_REF')
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
        data = models.modelo_inform(cursor, modelo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Modelo não encontrado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = '/produto/ref/{}'.format(row['REF'])
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


class ListaProduto(View):
    Form_class = FiltroForm
    template_name = 'produto/lista_produto.html'
    title_name = 'Listagem de produtos'

    def mount_context(self, cursor, busca):
        context = {'busca': busca}

        # Informações básicas
        data = models.lista_produto(cursor, busca)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum produto selecionado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = '/produto/ref/{}'.format(row['REF'])
            context.update({
                'headers': ('#', 'Tipo', 'Referência', 'Descrição',
                            'Status (Responsável)'),
                'fields': ('NUM', 'TIPO', 'REF', 'DESCR',
                           'RESP'),
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, busca))
        context['form'] = form
        return render(request, self.template_name, context)


class EstrEstagioDeInsumo(View):
    Form_class = FiltroForm
    template_name = 'produto/estr_estagio_de_insumo.html'
    title_name = 'Estágio de insumo'

    def mount_context(self, cursor):
        context = {}

        # Informações básicas
        data = models.estr_estagio_de_insumo(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum erro de estágio de insumo encontrado.',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = '/produto/ref/{}'.format(row['REF'])
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
