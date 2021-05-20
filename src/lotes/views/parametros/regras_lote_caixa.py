from pprint import pprint

from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import has_permission

import systextil.models

import lotes.forms as forms
import lotes.models
from lotes.models.functions.sync_regra_colecao import sync_regra_colecao
from lotes.views.parametros_functions import *


class RegrasLoteCaixa(View):

    def __init__(self):
        self.Form_class = forms.RegrasLoteCaixaForm
        self.template_name = 'lotes/regras_lote_caixa.html'
        self.title_name = 'Lotes por caixa'
        self.id = None
        self.context = {'titulo': self.title_name}

    def lista(self):
        sync_regra_colecao()

        col_list = systextil.models.Colecao.objects.exclude(
                colecao=0).values()
        colecao = {c['colecao']: c['descr_colecao'] for c in col_list}

        regras = lotes.models.RegraColecao.objects_referencia.all(
            ).order_by('colecao', 'referencia').values()

        for row in regras:
            row['descr_colecao'] = colecao[row['colecao']]
            if not row['referencia']:
                row['referencia'] = '-'
            link = reverse(
                'producao:regras_lote_caixa__get',
                args=[
                    row['colecao'],
                    row['referencia'],
                ]
            )
            row['edit'] = ('<a title="Editar" '
                         f'href="{link}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         )

        headers = ['Coleção', 'Descrição', 'Referência', 'Lote por caixa']
        fields = ['colecao', 'descr_colecao', 'referencia', 'lotes_caixa']
        if has_permission(self.request, 'lotes.change_leadcolecao'):
            headers.insert(0, '')
            fields.insert(0, 'edit')
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': regras,
            'safe': ['edit'],
        })


    def edit(self, num_colecao, referencia):
        if referencia == '-':
            referencia = ''
        print(f"'{referencia}'")
        try:
            lc = lotes.models.RegraColecao.objects_referencia.get(
                colecao=num_colecao, referencia=referencia)
        except lotes.models.RegraColecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Regra de coleção e referência não encontrados',
            })
            return

        try:
            colecao = systextil.models.Colecao.objects.get(
                colecao=num_colecao)
        except systextil.models.Colecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Coleção não encontrada',
            })
            return

        if referencia and len(referencia) < 5 and '%' not in referencia:
            referencia = f'{referencia}%'

        self.context['colecao'] = num_colecao
        self.context['referencia'] = referencia
        self.context['descr_colecao'] = colecao.descr_colecao
        self.context['form'] = self.Form_class(
            initial={
                'lotes_caixa': lc.lotes_caixa,
            })

    def get(self, request, *args, **kwargs):
        self.request = request

        if 'referencia' in kwargs and has_permission(request, 'lotes.change_leadcolecao'):
            self.edit(kwargs['colecao'], kwargs['referencia'])
        else:
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
                lc = lotes.models.RegraColecao.objects.get(colecao=self.id)
            except lotes.models.RegraColecao.DoesNotExist:
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
