from pprint import pprint

from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import has_permission

import systextil.models

import lotes.forms as forms
import lotes.models as models
from lotes.models.functions.sync_regra_colecao import sync_regra_colecao


class LoteMinColecao(View):

    def __init__(self):
        self.Form_class = forms.LoteMinColecaoForm
        self.template_name = 'lotes/lote_min_colecao.html'
        self.title_name = 'Lote mínimo por coleção'
        self.id = None
        self.context = {'titulo': self.title_name}

    def lista(self):
        sync_regra_colecao()

        col_list = systextil.models.Colecao.objects.exclude(
                colecao=0).values()
        colecao = {c['colecao']: c['descr_colecao'] for c in col_list}

        regras = models.RegraColecao.objects.all().order_by('colecao').values()

        for row in regras:
            row['descr_colecao'] = colecao[row['colecao']]

            row['edit'] = ('<a title="Editar" '
                         'href="{}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         ).format(reverse(
                            'producao:lote_min_colecao', args=[row['colecao']]))

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
            'data': regras,
            'safe': ['edit'],
        })

    def get(self, request, *args, **kwargs):
        self.request = request

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id:
            if has_permission(request, 'lotes.change_leadcolecao'):
                try:
                    lc = models.RegraColecao.objects.get(colecao=self.id)
                except models.RegraColecao.DoesNotExist:
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
                lc = models.RegraColecao.objects.get(colecao=self.id)
            except models.RegraColecao.DoesNotExist:
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
                self.context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                    'o lotes mínimos. <{}>'.format(str(e))

            self.lista()
        else:
            self.context['form'] = form
        return render(self.request, self.template_name, self.context)
