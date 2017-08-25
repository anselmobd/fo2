from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
# from django.template.defaultfilters import lower
from django.template.defaulttags import register

from fo2.models import rows_to_dict_list

from .forms import RefForm
import produto.models as models


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def index(request):
    context = {}
    return render(request, 'produto/index.html', context)


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
          AND (  ptc.PRECO_MEDIO IN NULL
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
            context.update({
                'headers': ('Descrição',),
                'fields': ('DESCR',),
                'data': data,
            })

            # Cores
            c_data = models.ref_cores(cursor, ref)
            if len(c_data) != 0:
                context.update({
                    'c_headers': ('Cor', 'Descrição'),
                    'c_fields': ('COR', 'DESCR'),
                    'c_data': c_data,
                })

        return context

    def get(self, request, *args, **kwargs):
        if 'ref' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context = self.mount_context(cursor, ref)
        context['form'] = form
        return render(request, self.template_name, context)
