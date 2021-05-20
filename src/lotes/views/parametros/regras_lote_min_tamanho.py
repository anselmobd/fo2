from operator import itemgetter
from pprint import pprint

from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from geral.functions import has_permission

import systextil.models

import lotes.forms as forms
import lotes.models as models
from lotes.views.parametros_functions import *


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
                self.context.update({
                    'msg_erro': 
                        (
                            'Ocorreu um erro ao gravar '
                            'o lotes mínimos. <{}>'
                        ).format(str(e)),
                })

            self.lista()
        else:
            self.context['form'] = form
        return redirect('producao:regras_lote_min_tamanho')
