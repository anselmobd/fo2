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
        self.Form_class_add = forms.AddRegrasLoteCaixaForm
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
            link_e = reverse(
                'producao:regras_lote_caixa__get',
                args=[
                    row['colecao'],
                    row['referencia'],
                    'e',
                ]
            )
            link_d = reverse(
                'producao:regras_lote_caixa__get',
                args=[
                    row['colecao'],
                    row['referencia'],
                    'd',
                ]
            )
            row['ead'] = (
                '<a title="Editar" '
                f'href="{link_e}">'
                '<span class="glyphicon glyphicon-pencil" '
                'aria-hidden="true"></span></a>'
                '&nbsp;&nbsp;&nbsp;'
                '<a title="Apagar" '
                f'href="{link_d}" '
                'onclick="return confirm(\'Confirma apagar?\');">'
                '<span class="glyphicon glyphicon-remove" '
                'aria-hidden="true"></span></a>'
            )

        headers = ['Coleção', 'Descrição', 'Referência', 'Lote por caixa']
        fields = ['colecao', 'descr_colecao', 'referencia', 'lotes_caixa']
        if has_permission(self.request, 'lotes.change_leadcolecao'):
            headers.insert(0, '')
            fields.insert(0, 'ead')
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': regras,
            'safe': ['ead'],
        })


    def add(self, form):
        self.context.update({
            'ead': 'a',
            'colecao': '-',
            'referencia': '-',
            'form': form,
        })

    def edit(self, num_colecao, referencia):
        referencia_filter = referencia
        if referencia_filter == '-':
            referencia_filter = ''

        try:
            rc = lotes.models.RegraColecao.objects_referencia.get(
                colecao=num_colecao, referencia=referencia_filter)
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

        self.context.update({
            'ead': 'e',
            'colecao': num_colecao,
            'referencia': referencia,
            'descr_colecao': colecao.descr_colecao,
            'form': self.Form_class(
                initial={
                    'lotes_caixa': rc.lotes_caixa,
                }
            ),
        })

    def get(self, request, *args, **kwargs):
        self.request = request

        if 'ead' in kwargs and has_permission(request, 'lotes.change_leadcolecao'):
            if kwargs['ead'] == 'e':
                self.edit(
                    kwargs['colecao'],
                    kwargs['referencia'],
                )
            elif kwargs['ead'] == 'a':
                self.add(self.Form_class_add())
            else:
                referencia_filter = kwargs['referencia']
                if referencia_filter == '-':
                    referencia_filter = ''

                try:
                    rc = lotes.models.RegraColecao.objects_referencia.get(
                        colecao=kwargs['colecao'], referencia=referencia_filter)
                except lotes.models.RegraColecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Regra de coleção e referência não encontrados',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                try:
                    rc.delete()
                except IntegrityError as e:
                    self.context.update({
                        'msg_erro': 'Ocorreu um erro ao apagar regra de coleção.',
                    })

                self.lista()
        else:
            self.lista()

        return render(self.request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request

        if not ('ead' in kwargs and
                has_permission(request, 'lotes.change_leadcolecao')
                ):
            self.lista()
        else:
            if kwargs['ead'] == 'e':
                form = self.Form_class(request.POST)
            elif kwargs['ead'] == 'a':
                form = self.Form_class_add(request.POST)

            if not form.is_valid():
                if kwargs['ead'] == 'e':
                    self.edit(
                        kwargs['colecao'],
                        kwargs['referencia'],
                    )
                elif kwargs['ead'] == 'a':
                    self.add(form)
                else:
                    self.lista()
                self.context['form'] = form
            else:
                lotes_caixa = form.cleaned_data['lotes_caixa']

                if kwargs['ead'] == 'e':
                    referencia_filter = kwargs['referencia']
                    if referencia_filter == '-':
                        referencia_filter = ''

                    try:
                        rc = lotes.models.RegraColecao.objects_referencia.get(
                            colecao=kwargs['colecao'], referencia=referencia_filter)
                    except lotes.models.RegraColecao.DoesNotExist:
                        self.context.update({
                            'msg_erro': 'Regra de coleção e referência não encontrados',
                        })
                        return render(
                            self.request, self.template_name, self.context)

                    try:
                        rc.lotes_caixa = lotes_caixa
                        rc.save()
                    except IntegrityError as e:
                        self.context.update({
                            'msg_erro': 'Ocorreu um erro ao gravar regra de coleção.',
                        })

                if kwargs['ead'] == 'a':
                    colecao = form.cleaned_data['colecao']
                    referencia = form.cleaned_data['referencia']
                    pprint(colecao.colecao)
                    pprint(referencia)
                    try:
                        rc = lotes.models.RegraColecao()
                        rc.colecao = colecao.colecao
                        rc.referencia = referencia
                        rc.lotes_caixa = lotes_caixa
                        rc.save()
                    except IntegrityError as e:
                        self.context.update({
                            'msg_erro': 'Ocorreu um erro ao gravar regra de coleção.',
                        })

                self.lista()
        return render(self.request, self.template_name, self.context)
