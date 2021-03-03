from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connections
from django.db.models import Exists, OuterRef
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from geral.functions import has_permission
from utils.views import totalize_grouped_data, totalize_data

import comercial.models
import produto.models
import produto.queries
import systextil.models
from comercial.views.estoque import grade_meta_estoque

import lotes.forms as forms
import lotes.models as models
import lotes.queries as queries
import lotes.views.a_produzir


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

        data = queries.analise.quant_estagio(cursor, estagio, ref, tipo)
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
            colecoes = systextil.models.Colecao.objects.exclude(
                colecao=0).order_by('colecao')
        except systextil.models.Colecao.DoesNotExist:
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
                    colecao = systextil.models.Colecao.objects.get(
                        colecao=self.id)
                except systextil.models.Colecao.DoesNotExist:
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

                cursor = db_cursor_so(request)
                calculaMetaGiroTodas(cursor)

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
            colecoes = systextil.models.Colecao.objects.exclude(
                colecao=0).order_by('colecao')
        except systextil.models.Colecao.DoesNotExist:
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
                    colecao = systextil.models.Colecao.objects.get(
                        colecao=self.id)
                except systextil.models.Colecao.DoesNotExist:
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
            tamanhos = systextil.models.Tamanho.objects.all(
                ).order_by('tamanho_ref')
        except systextil.models.Tamanho.DoesNotExist:
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
                    tamanho = systextil.models.Tamanho.objects.get(
                        tamanho_ref=self.id)
                except systextil.models.Tamanho.DoesNotExist:
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


def calculaMetaGiroTodas(cursor):
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


def calculaMetaTotalMetas(cursor, metas):
    metas_list = []
    total = 0
    for meta in metas:
        lead = produto.queries.lead_de_modelo(cursor, meta.modelo)
        qtd = 0

        ggrade = grade_meta_giro(meta, lead, show_distrib=False)
        qtd += ggrade['meta_giro']

        egrade = grade_meta_estoque(meta)
        qtd += egrade['meta_estoque']

        total += qtd

        grade = lotes.views.a_produzir.soma_grades(ggrade, egrade)

        metas_list.append({
            'modelo': meta.modelo,
            'qtd': qtd,
            'grade': grade,
        })
    return metas_list, total


class MetaTotal(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(MetaTotal, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/meta_total.html'
        self.title_name = 'Visualiza total das metas'

    def mount_context(self):
        cursor = connections['so'].cursor()

        metas = comercial.models.getMetaEstoqueAtual()
        metas = metas.order_by('-venda_mensal')
        if len(metas) == 0:
            self.context.update({
                'msg_erro': 'Sem metas definidas',
            })
            return

        metas_list, total = calculaMetaTotalMetas(cursor, metas)

        self.context.update({
            'data': metas_list,
            'total': total,
        })
