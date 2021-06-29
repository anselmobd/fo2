import re
import urllib
from pprint import pformat, pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from geral.functions import has_permission
from geral.views import dict_colecao_fluxos, get_roteiros_de_fluxo
from utils.forms import FiltroForm
from utils.functions.models import rows_to_dict_list
from utils.views import group_rowspan

import produto.forms as forms
import produto.queries as queries


def index(request):
    return render(request, 'produto/index.html')


def lista_item_n1_sem_preco_medio(request):
    context = {
        'titulo': 'Produto',
        'urltitulo': '/produto/',
        'subtitulo': 'Itens de nível 1 sem definição de preço médio',
    }
    cursor = db_cursor_so(request)
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


def estatistica(request):
    cursor = db_cursor_so(request)
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
    cursor = db_cursor_so(request)

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
    cursor = db_cursor_so(request)
    if nivel[0:4] in ('1-MD', '1-PB', '1-PG', '1-PA', '1-MP'):
        data = queries.produtos_n1_basic(cursor, nivel[2:])
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


class Busca(View):
    Form_class = forms.FiltroRefForm
    template_name = 'produto/busca.html'
    title_name = 'Listagem de produtos'

    def mount_context(self, cursor, filtro, cor, roteiro, alternativa):
        context = {'filtro': filtro}

        if roteiro is None:
            roteiro = 0
        if alternativa is None:
            alternativa = 0
        data = queries.busca_produto(cursor, filtro, cor, roteiro, alternativa)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum produto selecionado',
            })
        else:
            for row in data:
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
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
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'filtro' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'filtro' in kwargs:
            form.data['filtro'] = kwargs['filtro']
        if form.is_valid():
            filtro = form.cleaned_data['filtro']
            cor = form.cleaned_data['cor']
            roteiro = form.cleaned_data['roteiro']
            alternativa = form.cleaned_data['alternativa']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, filtro, cor, roteiro, alternativa))
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
        cursor = db_cursor_so(request)
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)


class MultiplasColecoes(View):
    Form_class = FiltroForm
    template_name = 'produto/multiplas_colecoes.html'
    title_name = 'Múltiplas coleções em modelo'

    def mount_context(self, cursor):
        context = {}

        # Informações básicas
        data = queries.multiplas_colecoes(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum erro de múltiplas coleções em modelos.',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])

            group = ['MODELO', 'COLECOES']
            group_rowspan(data, group)

            context.update({
                'headers': ('Modelo', 'Nº coleções', 'Coleção', 'Descrição',
                            'Referência', 'Descrição'),
                'fields': ('MODELO', 'COLECOES', 'COLECAO', 'DESCR_COLECAO',
                           'REF', 'DESCR'),
                'data': data,
                'link': link,
                'group': group,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = db_cursor_so(request)
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)


class RoteirosPadraoRef(View):
    Form_class = forms.GeraRoteirosRefForm
    template_name = 'produto/roteiros_padrao_ref.html'
    title_name = 'Roteiros padrão por referência'

    def mount_context(self, cursor, ref):
        if ref == '':
            return {}

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
        if 'ref' in kwargs and kwargs['ref'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'ref' in kwargs and kwargs['ref'] is not None:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)


def gera_roteiros_padrao_ref(cursor, ref):
    roteiro_correto = 0
    roteiro_errado = 0
    gargalo_errado = 0

    data = queries.ref_inform(cursor, ref)

    info = data[0]
    tipo = info['TIPO'].lower()
    colecao = info['COLECAO']
    colecao_id = info['CODIGO_COLECAO']

    fluxos = dict_colecao_fluxos(colecao_id, tipo, ref)

    # pega dos fluxos os roteiros padrão
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
        # retira indicação de 'os', que não é um estágio
        roteiros[roteiro][0] = [
            est for est in roteiros[roteiro][0] if isinstance(est, int)]

        estagios = roteiros[roteiro][0]
        gargalo = roteiros[roteiro][1]
        output += '\nroteiro {}\n'.format(roteiro)
        output += 'padrao: '+pformat(roteiros[roteiro], indent=4)+'\n'

        # pega do DB de um número de roteiro específico as variações de
        # estrutura por tam. e cor
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

            # pega no DB os estágios de determinado roteiro, tam. e cor
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

            if estagios_db == roteiros[roteiro]:
                roteiro_correto += 1
            else:
                if estagios_db[0] != estagios:
                    roteiro_errado += 1
                    if len(estagios_db[0]) != 0:
                        output += '-> exclui estagios\n'
                        delete = queries.mount_delete_estagios(
                            roteiro, ref, tam, cor)
                        sqls.append(delete)
                    output += '-> inclui estagios\n'
                    inserts = queries.mount_inserts_estagios(
                        roteiro, ref, tam, cor, estagios)
                    for insert in inserts:
                        sqls.append(insert)
                else:
                    gargalo_errado += 1
                    if estagios_db[1] is not None:
                        output += '-> exclui gargalo {}\n'.format(
                            estagios_db[1])
                        unsetg = queries.mount_unset_gargalo(
                            roteiro, ref, tam, cor)
                        sqls.append(unsetg)
                output += '-> inclui gargalo {}\n'.format(gargalo)
                setg = queries.mount_set_gargalo(
                    roteiro, ref, tam, cor, gargalo)
                sqls.append(setg)

    # output += pformat(sqls, indent=4)+'\n'
    for sql in sqls:
        cursor.execute(sql)

    return output, [roteiro_correto, roteiro_errado, gargalo_errado]


class GeraRoteirosPadraoRef(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_generate_product_stages'

    def get(self, request, *args, **kwargs):
        ref = kwargs['ref']
        if ref is None:
            return HttpResponse('', content_type='text/plain')

        ref = ref.upper()
        cursor = db_cursor_so(request)

        quant = kwargs['quant']
        if quant is None:
            quant = 1
        else:
            try:
                quant = int(quant)
            except Exception:
                quant = 1

        roteiro_correto = 0
        roteiro_errado = 0
        gargalo_errado = 0

        output = ''
        refs = queries.get_refs(cursor)
        count = 0
        for referencia in refs:
            if referencia['REFERENCIA'] >= ref:
                count += 1
                if count <= quant:
                    output_ref, stat = gera_roteiros_padrao_ref(
                        cursor,
                        referencia['REFERENCIA'])
                    roteiro_correto += stat[0]
                    roteiro_errado += stat[1]
                    gargalo_errado += stat[2]
                    output += '\n\n= referencia: ' + \
                        referencia['REFERENCIA'] + '\n'
                    output += output_ref

        stats = 'Roteiros inalterados: {}\n' + \
                'Roteiros recriados: {}\n' + \
                'Gargalos corrigidos: {}\n'
        stats = stats.format(
                    roteiro_correto,
                    roteiro_errado,
                    gargalo_errado
                )
        output = stats + output
        context = {
            'titulo': 'Padronização de roteiros',
            'output': output,
        }
        template_name = 'produto/output.html'
        return render(request, template_name, context)
        # return HttpResponse(
        #     output,
        #     content_type='text/plain')


class InfoXml(View):
    Form_class = forms.ReferenciaForm
    template_name = 'produto/info_xml.html'
    title_name = 'Informações p/ NFe XML'

    def mount_context(self, cursor, ref):
        context = {'ref': ref}

        data = queries.info_xml(cursor, ref=ref)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            if row['SKU_INFADPROD'] is None:
                row['SKU_INFADPROD'] = '-'
            if row['SKU_NARRATIVA'] is None:
                row['SKU_NARRATIVA'] = '-'

        headers = [
            'Tamanho', 'Cor', 'GTIN',
            'SKU indAdProd', 'SKU Narrativa', 'Narrativa']
        fields = [
            'TAM', 'COR', 'GTIN',
            'SKU_INFADPROD', 'SKU_NARRATIVA', 'NARRATIVA']

        context.update({
            'ref_link': reverse('produto:ref__get', args=[row['REF']]),
            'cliente': data[0]['CLIENTE'],
            'cliente_link': reverse(
                'produto:por_cliente__get', args=[data[0]['CNPJ9']]),
            'headers': headers,
            'fields': fields,
            'data': data,
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
        form.data = form.data.copy()
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)


class PorCliente(View):
    Form_class = forms.ClienteForm
    template_name = 'produto/por_cliente.html'
    title_name = 'Por cliente'

    def mount_context(self, cursor, cliente):
        context = {'cliente': cliente}

        data = queries.por_cliente(cursor, cliente=cliente)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            row['REF|LINK'] = reverse(
                'produto:info_xml__get', args=[row['REF']])

        headers = [
            'Referência', 'Descrição', 'Cliente']
        fields = [
            'REF', 'DESCR', 'CLIENTE']

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'cliente' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'cliente' in kwargs:
            form.data['cliente'] = kwargs['cliente']
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, cliente))
        context['form'] = form
        return render(request, self.template_name, context)
