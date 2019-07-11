from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin

from geral.functions import has_permission
from base.views import O2BaseGetView
from utils.views import totalize_grouped_data

import produto.queries
import produto.models
import comercial.models

import lotes.forms as forms
import lotes.models as models


class TotalEstagio(View):
    Form_class = forms.TotaisEstagioForm
    template_name = 'lotes/total_estagio.html'
    title_name = 'Totais gerais dos estágios'

    def mount_context(self, cursor, tipo_roteiro, cliente, deposito):
        context = {
            'tipo_roteiro': tipo_roteiro,
            'deposito': deposito,
        }

        if cliente:
            data_c = produto.queries.busca_cliente_de_produto(cursor, cliente)
            if len(data_c) == 1:
                row = data_c[0]
                cnpj9 = row['cnpj9']
                cliente_full = '{:08d}/{:04d}-{:02d} {}'.format(
                    row['cnpj9'],
                    row['cnpj4'],
                    row['cnpj2'],
                    row['cliente'],
                )
                context.update({
                    'cliente': cliente,
                    'cliente_full': cliente_full,
                })
            else:
                context.update({
                    'msg_erro': 'Cliente não encontrado',
                })
                return context
        else:
            cnpj9 = None

        data = models.totais_estagios(cursor, tipo_roteiro, cnpj9, deposito)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem quantidades',
            })
            return context

        def mount_dict(dic, pre, sep, pos):
            for pr in pre:
                for po in pos:
                    dic.append(pr+(sep if po else '')+po)
            return dic

        produtos = ['PA', 'PG', 'PB']
        headers = mount_dict(
            ['Estágio'], ['Lotes', 'Itens', 'Peças'],
            ' ', produtos + ['MD', 'MP', ''])
        quant_fields = mount_dict(
            [], ['LOTES', 'QUANT', 'PECAS'],
            '_', produtos + ['MD', 'MP', ''])
        fields = ['ESTAGIO'] + quant_fields

        giro_lotes = mount_dict([], ['LOTES'], '_', produtos)
        giro_quant = mount_dict([], ['QUANT'], '_', produtos)
        giro_pecas = mount_dict([], ['PECAS'], '_', produtos)
        nao_giro_lotes = mount_dict([], ['LOTES'], '_', ['MD', 'MP'])
        nao_giro_quant = mount_dict([], ['QUANT'], '_', ['MD', 'MP'])
        nao_giro_pecas = mount_dict([], ['PECAS'], '_', ['MD', 'MP'])
        nao_giro_fields = nao_giro_lotes+nao_giro_quant+nao_giro_pecas

        style_r = 'text-align: right;'
        style_bl = 'border-left-style: solid; border-left-width: ' \
            'thin; border-color: lightgray;'
        style_bl_sep = 'border-left-style: double; border-left-width: ' \
            'thick; border-color: lightgray;'
        style_b = 'font-weight: bold;'
        style = {}
        for i in range(2, 20):
            if i in [7, 13, 19]:
                style[i] = style_r + style_b + style_bl
            elif i in [8, 14]:
                style[i] = style_r + style_bl_sep
            else:
                style[i] = style_r + style_bl

        context.update({
            'headers': headers,
            'fields': fields,
            'style': style,
        })

        estagio_programacao = [3]
        estagio_estoque = [57, 60, 63]
        estagio_vendido = [66]
        estagio_nao_producao = \
            estagio_programacao + estagio_estoque + estagio_vendido

        def red_columns(dicti):
            for field in ['LOTES', 'QUANT', 'PECAS']:
                dicti['{}|STYLE'.format(field)] = 'color: red;'

        def init_total(titulo, dicti, subtotal=False):
            total_dict = dicti[0].copy()
            total_dict['ESTAGIO'] = titulo
            for field in quant_fields:
                total_dict[field] = 0
            if not subtotal:
                total_dict['|STYLE'] = 'font-weight: bold;'
                red_columns(total_dict)
            return total_dict

        def soma_fields(tot_dict, data, fields):
            for row in data:
                for field in fields:
                    tot_dict[field] += row[field]

        data_p = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_programacao]
        if len(data_p) > 0:
            red_columns(data_p[0])
            context.update({
                'data_p': data_p,
            })

        data_d = [
            r for r in data if r['CODIGO_ESTAGIO'] not in estagio_nao_producao]
        total_producao_giro = None
        if len(data_d) > 0:
            total_producao = init_total('Total em produção', data_d)
            total_producao_giro = init_total(
                'Total em produção (giro)', data_d, subtotal=True)
            soma_fields(total_producao, data_d, quant_fields)
            soma_fields(
                total_producao_giro, data_d, giro_lotes+giro_quant+giro_pecas)
            data_d.append(total_producao)
            context.update({
                'data_d': data_d,
            })

        data_e = [r for r in data if r['CODIGO_ESTAGIO'] in estagio_estoque]
        total_estoque_giro = None
        if len(data_e) > 0:
            total_estoque = init_total('Total em estoque', data_e)
            total_estoque_giro = init_total(
                'Total em estoque', data_e, subtotal=True)
            soma_fields(total_estoque, data_e, quant_fields)
            soma_fields(
                total_estoque_giro, data_e, giro_lotes+giro_quant+giro_pecas)
            data_e.append(total_estoque)
            context.update({
                'data_e': data_e,
            })

        data_v = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_vendido]
        if len(data_v) > 0:
            red_columns(data_v[0])
            context.update({
                'data_v': data_v,
            })

        total_geral = init_total('Total geral', data)
        soma_fields(total_geral, data, quant_fields)
        context.update({
            'data_t': [total_geral],
        })

        def soma_row_columns(dicti, tot_field, fields):
            for column in fields:
                dicti[tot_field] += dicti[column]

        def soma_os_3_totais(dicti):
            soma_row_columns(dicti, 'LOTES', giro_lotes)
            soma_row_columns(dicti, 'QUANT', giro_quant)
            soma_row_columns(dicti, 'PECAS', giro_pecas)

        data_giro = []
        if total_producao_giro is not None:
            soma_os_3_totais(total_producao_giro)
            data_giro.append(total_producao_giro)
        if total_estoque_giro is not None:
            soma_os_3_totais(total_estoque_giro)
            data_giro.append(total_estoque_giro)

        if len(data_giro) > 0:
            total_giro = init_total('Total em giro', data_giro)
            soma_fields(total_giro, data_giro, quant_fields)
            data_giro.append(total_giro)

            headers_g = headers.copy()
            for field in nao_giro_fields:
                headers_g[fields.index(field)] = '-'
            for row in data_giro:
                for field in nao_giro_fields:
                    row[field] = ' '

            context.update({
                'headers_g': headers_g,
                'data_g': data_giro,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        tipo_roteiro = 'p'
        cliente = ''
        deposito = ''
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(cursor, tipo_roteiro, cliente, deposito))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            tipo_roteiro = form.cleaned_data['tipo_roteiro']
            cliente = form.cleaned_data['cliente']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, tipo_roteiro, cliente, deposito))
        context['form'] = form
        return render(request, self.template_name, context)


class QuantEstagio(View):
    Form_class = forms.QuantEstagioForm
    template_name = 'lotes/quant_estagio.html'
    title_name = 'Quantidades por estágio'

    def mount_context(self, cursor, estagio, ref, tipo):
        context = {
            'estagio': estagio,
            'ref': ref,
            'tipo': tipo,
        }

        data = models.quant_estagio(cursor, estagio, ref, tipo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produtos no estágio',
            })
            return context

        total = data[0].copy()
        total['REF'] = ''
        total['TAM'] = ''
        total['COR'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fields = ['LOTES', 'QUANT']
        for field in quant_fields:
            total[field] = 0
        for row in data:
            for field in quant_fields:
                total[field] += row[field]
        data.append(total)
        context.update({
            'headers': ('Produto', 'Tamanho', 'Cor', 'Lotes', 'Quantidade'),
            'fields': ('REF', 'TAM', 'COR', 'LOTES', 'QUANT'),
            'data': data,
            'style': {4: 'text-align: right;',
                      5: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'estagio' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'estagio' in kwargs:
            form.data['estagio'] = kwargs['estagio']
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            ref = form.cleaned_data['ref']
            tipo = form.cleaned_data['tipo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, estagio, ref, tipo))
        context['form'] = form
        return render(request, self.template_name, context)


class LeadColecao(View):

    def __init__(self):
        self.Form_class = forms.LeadColecaoForm
        self.template_name = 'lotes/lead_colecao.html'
        self.title_name = 'Lead de produção por coleção'
        self.id = None
        self.context = {'titulo': self.title_name}

    def lista(self):
        try:
            colecoes = produto.models.Colecao.objects.exclude(
                colecao=0).order_by('colecao')
        except produto.models.Colecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Coleções não encontradas',
            })
            return

        try:
            LC = models.LeadColecao.objects.all().order_by('colecao')
        except models.LeadColecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Leads de coleções não encontradas',
            })
            return

        lcs = {}
        inter_col = colecoes.iterator()
        inter_LC = LC.iterator()
        walk = 'b'   # from, to, both
        while True:
            if walk in ['f', 'b']:
                try:
                    col = next(inter_col)
                except StopIteration:
                    col = None

            if walk in ['t', 'b']:
                try:
                    lc = next(inter_LC)
                except StopIteration:
                    lc = None

            if lc is None and col is None:
                break

            rec = {
                'descr_colecao': '',
                'lead': 0,
            }
            acao_definida = False

            if lc is not None:
                if col is None or col.colecao > lc.colecao:
                    acao_definida = True
                    rec['status'] = 'd'
                    rec['colecao'] = lc.colecao
                    walk = 't'

            if not acao_definida:
                rec['colecao'] = col.colecao
                rec['descr_colecao'] = col.descr_colecao
                if lc is None or col.colecao < lc.colecao:
                    acao_definida = True
                    rec['status'] = 'i'
                    walk = 'f'

            if not acao_definida:
                rec['lead'] = lc.lead
                rec['status'] = 'u'
                walk = 'b'

            lcs[rec['colecao']] = rec

        data = []
        for key in lcs:
            if lcs[key]['status'] == 'd':
                try:
                    models.LeadColecao.objects.filter(colecao=key).delete()
                except models.LeadColecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Erro apagando lead',
                    })
                    return
                continue

            if lcs[key]['status'] == 'i':
                try:
                    lc = models.LeadColecao()
                    lc.colecao = key
                    lc.lead = 0
                    lc.save()
                except Exception:
                    self.context.update({
                        'msg_erro': 'Erro salvando lead',
                    })
                    return
            lcs[key].update({
                'edit': ('<a title="Editar" '
                         'href="{}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         ).format(reverse(
                            'producao:lead_colecao', args=[key])),
            })
            data.append(lcs[key])

        headers = ['Coleção', 'Descrição', 'Lead (dias)']
        fields = ['colecao', 'descr_colecao', 'lead']
        if has_permission(self.request, 'lotes.change_leadcolecao'):
            headers.insert(0, '')
            fields.insert(0, 'edit')
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'safe': ['edit'],
        })

    def get(self, request, *args, **kwargs):
        self.request = request

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id:
            if has_permission(request, 'lotes.change_leadcolecao'):
                try:
                    lc = models.LeadColecao.objects.get(colecao=self.id)
                except models.LeadColecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Lead não encontrado',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                try:
                    colecao = produto.models.Colecao.objects.get(
                        colecao=self.id)
                except produto.models.Colecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Coleção não encontrada',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                self.context['id'] = self.id
                self.context['descr_colecao'] = colecao.descr_colecao
                self.context['form'] = self.Form_class(
                    initial={'lead': lc.lead})
            else:
                self.id = None

        if not self.id:
            self.lista()

        return render(self.request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request

        if 'id' in kwargs:
            self.id = kwargs['id']

        form = self.Form_class(request.POST)
        if self.id and form.is_valid():
            lead = form.cleaned_data['lead']

            try:
                lc = models.LeadColecao.objects.get(colecao=self.id)
            except models.LeadColecao.DoesNotExist:
                self.context.update({
                    'msg_erro': 'Lead não encontrado',
                })
                return render(
                    self.request, self.template_name, self.context)

            try:
                lc.lead = lead
                lc.save()
            except IntegrityError as e:
                context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                    'o lead. <{}>'.format(str(e))

            self.lista()
        else:
            self.context['form'] = form
        return render(self.request, self.template_name, self.context)


class MetaGiro(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaGiro, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_giro.html'
        self.title_name = 'Visualiza meta de giro'

    def mount_context(self):
        cursor = connections['so'].cursor()

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list = list(metas.values())
        for meta in metas_list:
            colecao = produto.queries.colecao_de_modelo(cursor, meta['modelo'])
            if colecao == -1:
                lead = 0
            else:
                try:
                    lc = models.LeadColecao.objects.get(colecao=colecao)
                    lead = lc.lead
                except models.LeadColecao.DoesNotExist:
                    lead = 0

            meta['lead'] = lead
            meta['giro'] = round(meta['venda_mensal'] / 30 * meta['lead'])

        for meta in metas:
            grade = {}

            grade['headers'] = ['Cor/Tamanho']
            grade['fields'] = ['cor']
            meta_tamanhos = comercial.models.MetaEstoqueTamanho.objects.filter(
                meta=meta).order_by('ordem')
            meta_grade_tamanhos = {}
            tot_tam = 0
            qtd_por_tam = {}
            grade['style'] = {
                1: 'text-align: left;',
            }
            for tamanho in meta_tamanhos:
                if tamanho.quantidade != 0:
                    grade['headers'].append(tamanho.tamanho)
                    grade['fields'].append(tamanho.tamanho)
                    meta_grade_tamanhos[tamanho.tamanho] = tamanho.quantidade
                    tot_tam += tamanho.quantidade
                    qtd_por_tam[tamanho.tamanho] = 0
                    grade['style'][max(grade['style'].keys())+1] = \
                        'text-align: right;'
            grade['style'][max(grade['style'].keys())+1] = \
                'text-align: right; font-weight: bold;'

            qtd_por_tam['total'] = meta.venda_mensal

            grade['headers'].append('Total')
            grade['fields'].append('total')
            tot_packs = meta.venda_mensal / tot_tam

            meta_cores = comercial.models.MetaEstoqueCor.objects.filter(
                meta=meta).order_by('cor')
            meta_grade_cores = {}
            tot_cor = 0
            for cor in meta_cores:
                meta_grade_cores[cor.cor] = cor.quantidade
                tot_cor += cor.quantidade

            grade['data'] = []
            for meta_cor in meta_grade_cores:
                if meta_grade_cores[meta_cor] != 0:
                    linha = {
                        'cor': meta_cor,
                    }
                    cor_packs = round(
                        tot_packs / tot_cor * meta_grade_cores[meta_cor])
                    for meta_tam in meta_grade_tamanhos:
                        qtd_cor_tam = cor_packs * meta_grade_tamanhos[meta_tam]
                        linha.update({
                            meta_tam: round(qtd_cor_tam),
                        })
                        qtd_por_tam[meta_tam] += qtd_cor_tam
                    linha['total'] = cor_packs * tot_tam
                    grade['data'].append(linha)
            grade['data'].append({
                'cor': 'Total',
                **qtd_por_tam,
                '|STYLE': 'font-weight: bold;',
            })

            idx_meta = [idx for idx, item in enumerate(metas_list)
                        if item['modelo'] == meta.modelo][0]
            metas_list[idx_meta].update({
                'grade': grade,
            })

        group = ['modelo']
        totalize_grouped_data(metas_list, {
            'group': group,
            'flags': ['NO_TOT_1'],
            'global_sum': ['giro'],
            'sum': ['giro'],
            'count': [],
            'descr': {'modelo': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Modelo', 'Data', 'Venda mensal', 'Lead',
                        'Meta de giro'],
            'fields': ['modelo', 'data', 'venda_mensal', 'lead',
                       'giro'],
            'data': metas_list,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
            'total': metas_list[-1]['giro'],
        })
