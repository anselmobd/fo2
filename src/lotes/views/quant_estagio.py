from pprint import pprint
from operator import itemgetter

from django.shortcuts import render, redirect
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
        self.title_name = 'Lead por coleção'
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
                'msg_erro': 'Parâmetros de coleções não encontrados',
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
                        'msg_erro': 'Erro apagando parâmetros de coleção',
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
                        'msg_erro': 'Parâmetros de coleção não encontrados',
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
                    'msg_erro': 'Parâmetros de coleção não encontrados',
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


class LoteMinColecao(View):

    def __init__(self):
        self.Form_class = forms.LoteMinColecaoForm
        self.template_name = 'lotes/lote_min_colecao.html'
        self.title_name = 'Lote mínimo por coleção'
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
                'msg_erro': 'Parâmetros de coleções não encontrados',
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
                'lm_tam': 0,
                'lm_cor': 0,
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
                rec['lm_tam'] = lc.lm_tam
                rec['lm_cor'] = lc.lm_cor
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
                        'msg_erro': 'Erro apagando parâmetros de coleção',
                    })
                    return
                continue

            if lcs[key]['status'] == 'i':
                try:
                    lc = models.LeadColecao()
                    lc.colecao = key
                    lc.lm_tam = 0
                    lc.lm_cor = 0
                    lc.save()
                except Exception:
                    self.context.update({
                        'msg_erro': 'Erro salvando lote mínimo',
                    })
                    return
            lcs[key].update({
                'edit': ('<a title="Editar" '
                         'href="{}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         ).format(reverse(
                            'producao:lote_min_colecao', args=[key])),
            })
            data.append(lcs[key])

        headers = ['Coleção', 'Descrição',
                   'Lote mínimo por tamanho', 'Lote mínimo por cor']
        fields = ['colecao', 'descr_colecao',
                  'lm_tam', 'lm_cor']
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
                        'msg_erro': 'Parâmetros de coleção não encontrados',
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
                    initial={
                        'lm_tam': lc.lm_tam,
                        'lm_cor': lc.lm_cor,
                    })
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
            lm_tam = form.cleaned_data['lm_tam']
            lm_cor = form.cleaned_data['lm_cor']

            try:
                lc = models.LeadColecao.objects.get(colecao=self.id)
            except models.LeadColecao.DoesNotExist:
                self.context.update({
                    'msg_erro': 'Parâmetros de coleção não encontrados',
                })
                return render(
                    self.request, self.template_name, self.context)

            try:
                lc.lm_tam = lm_tam
                lc.lm_cor = lm_cor
                lc.save()
            except IntegrityError as e:
                context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                    'o lotes mínimos. <{}>'.format(str(e))

            self.lista()
        else:
            self.context['form'] = form
        return render(self.request, self.template_name, self.context)


class RegrasLoteMinTamanho(View):

    def __init__(self):
        self.Form_class = forms.RegrasLoteMinTamanhoForm
        self.template_name = 'lotes/regras_lote_min_tamanho.html'
        self.title_name = 'Regras de lote mínimo por tamanho'
        self.id = None
        self.context = {'titulo': self.title_name}

    def lista(self):
        try:
            tamanhos = produto.models.S_Tamanho.objects.all(
                ).order_by('tamanho_ref')
        except produto.models.S_Tamanho.DoesNotExist:
            self.context.update({
                'msg_erro': 'Tamanhos não encontrados',
            })
            return

        try:
            RLM = models.RegraLMTamanho.objects.all(
                ).order_by('tamanho')
        except models.RegraLMTamanho.DoesNotExist:
            self.context.update({
                'msg_erro': 'Regras de lote mínimo não encontrados',
            })
            return

        regras = {}
        inter_tam = tamanhos.iterator()
        inter_RLM = RLM.iterator()
        walk = 'b'   # from, to, both
        while True:
            if walk in ['f', 'b']:
                try:
                    tam = next(inter_tam)
                except StopIteration:
                    tam = None

            if walk in ['t', 'b']:
                try:
                    rlm = next(inter_RLM)
                except StopIteration:
                    rlm = None

            if rlm is None and tam is None:
                break

            rec = {
                'min_para_lm': 0,
                'lm_cor_sozinha': 's',
            }
            acao_definida = False

            if rlm is not None:
                if tam is None or tam.tamanho_ref > rlm.tamanho:
                    acao_definida = True
                    rec['status'] = 'd'
                    rec['tamanho'] = rlm.tamanho
                    walk = 't'

            if not acao_definida:
                rec['tamanho'] = tam.tamanho_ref
                rec['ordem_tamanho'] = tam.ordem_tamanho
                if rlm is None or tam.tamanho_ref < rlm.tamanho:
                    acao_definida = True
                    rec['status'] = 'i'
                    walk = 'f'

            if not acao_definida:
                rec['min_para_lm'] = rlm.min_para_lm
                rec['lm_cor_sozinha'] = rlm.lm_cor_sozinha
                rec['status'] = 'u'
                walk = 'b'

            regras[rec['tamanho']] = rec

        data = []
        for key in regras:
            if regras[key]['status'] == 'd':
                try:
                    models.RegraLMTamanho.objects.filter(
                        tamanho=key).delete()
                except models.RegraLMTamanho.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Erro apagando regras de lote mínimo',
                    })
                    return
                continue

            if regras[key]['status'] == 'i':
                try:
                    rlm = models.RegraLMTamanho()
                    rlm.tamanho = key
                    rlm.ordem_tamanho = regras[key]['ordem_tamanho']
                    rlm.min_para_lm = regras[key]['min_para_lm']
                    rlm.lm_cor_sozinha = regras[key]['lm_cor_sozinha']
                    rlm.save()
                except Exception:
                    self.context.update({
                        'msg_erro': 'Erro salvando regras de lote mínimo',
                    })
                    return
            regras[key].update({
                'edit': ('<a title="Editar" '
                         'href="{}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         ).format(reverse(
                            'producao:regras_lote_min_tamanho', args=[key])),
            })
            data.append(regras[key])

        data = sorted(data, key=itemgetter('ordem_tamanho'))

        headers = ['Tamanho', 'Ordem do tamanho',
                   'Mínimo para aplicação do lote mínimo',
                   'Aplica lote mínimo por cor quando único tamanho']
        fields = ['tamanho', 'ordem_tamanho',
                  'min_para_lm',
                  'lm_cor_sozinha']
        if has_permission(self.request, 'lotes.change_regralmtamanho'):
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
            if has_permission(request, 'lotes.change_regralmtamanho'):
                try:
                    rlm = models.RegraLMTamanho.objects.get(tamanho=self.id)
                except models.RegraLMTamanho.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Regras de lote mínimo não encontradas',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                try:
                    tamanho = produto.models.S_Tamanho.objects.get(
                        tamanho_ref=self.id)
                except produto.models.S_Tamanho.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Tamanho não encontrado',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                self.context['id'] = self.id
                self.context['form'] = self.Form_class(
                    initial={
                        'min_para_lm': rlm.min_para_lm,
                        'lm_cor_sozinha': rlm.lm_cor_sozinha,
                    })
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
            min_para_lm = form.cleaned_data['min_para_lm']
            lm_cor_sozinha = form.cleaned_data['lm_cor_sozinha']

            try:
                rlm = models.RegraLMTamanho.objects.get(tamanho=self.id)
            except models.RegraLMTamanho.DoesNotExist:
                self.context.update({
                    'msg_erro': 'Parâmetros de coleção não encontrados',
                })
                return render(
                    self.request, self.template_name, self.context)

            try:
                rlm.min_para_lm = min_para_lm
                rlm.lm_cor_sozinha = lm_cor_sozinha
                rlm.save()
            except IntegrityError as e:
                context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                    'o lotes mínimos. <{}>'.format(str(e))

            self.lista()
        else:
            self.context['form'] = form
        return redirect('producao:regras_lote_min_tamanho')


def grade_meta_giro(meta, lead, show_distrib=True):
    meta_giro = round(
        meta.venda_mensal / 30 * lead)

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
            if show_distrib:
                grade['headers'].append(
                    '{}({})'.format(tamanho.tamanho, tamanho.quantidade))
            else:
                grade['headers'].append(tamanho.tamanho)
            grade['fields'].append(tamanho.tamanho)
            meta_grade_tamanhos[tamanho.tamanho] = tamanho.quantidade
            tot_tam += tamanho.quantidade
            qtd_por_tam[tamanho.tamanho] = 0
            grade['style'][max(grade['style'].keys())+1] = \
                'text-align: right;'

    resto = meta_giro % tot_tam
    if resto != 0:
        meta_giro = meta_giro + tot_tam - resto

    grade['headers'].append('Total')
    grade['fields'].append('total')
    grade['style'][max(grade['style'].keys())+1] = \
        'text-align: right; font-weight: bold;'

    tot_packs = meta_giro / tot_tam

    meta_cores = comercial.models.MetaEstoqueCor.objects.filter(
        meta=meta).order_by('cor')
    tot_cor = 0
    for cor in meta_cores:
        tot_cor += cor.quantidade

    grade['data'] = []
    meta_giro = 0
    for cor in meta_cores:
        if cor.quantidade != 0:
            if show_distrib:
                linha = {
                    'cor': '{}({})'.format(cor.cor, cor.quantidade),
                }
            else:
                linha = {
                    'cor': cor.cor,
                }
            cor_packs = round(
                tot_packs / tot_cor * cor.quantidade)
            for meta_tam in meta_grade_tamanhos:
                qtd_cor_tam = cor_packs * meta_grade_tamanhos[meta_tam]
                linha.update({
                    meta_tam: round(qtd_cor_tam),
                })
                qtd_por_tam[meta_tam] += qtd_cor_tam
            linha['total'] = cor_packs * tot_tam
            meta_giro += linha['total']
            grade['data'].append(linha)

    grade['meta_giro'] = meta_giro
    grade['data'].append({
        'cor': 'Total',
        **qtd_por_tam,
        'total': meta_giro,
        '|STYLE': 'font-weight: bold;',
    })
    return grade


def calculaMetaGiroTodas():
    cursor = connections['so'].cursor()

    metas = comercial.models.getMetaEstoqueAtual()
    if len(metas) == 0:
        return 0
    else:
        metas_list = calculaMetaGiroMetas(cursor, metas)
        return len(metas_list)


def calculaMetaGiroMetas(cursor, metas):
    metas_list = []
    for meta in metas:
        meta_dict = meta.__dict__
        metas_list.append(meta_dict)

        lead = produto.queries.lead_de_modelo(
            cursor, meta_dict['modelo'])

        grade = grade_meta_giro(meta, lead)

        meta_dict['lead'] = lead
        meta_dict['giro'] = grade['meta_giro']

        if meta.meta_giro != meta_dict['giro']:
            meta.meta_giro = meta_dict['giro']
            meta.save()

        meta_dict['grade'] = grade
    return metas_list


class MetaGiro(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaGiro, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_giro.html'
        self.title_name = 'Visualiza meta de giro'

    def mount_context(self):
        cursor = connections['so'].cursor()

        metas = comercial.models.getMetaEstoqueAtual()
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list = calculaMetaGiroMetas(cursor, metas)

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
