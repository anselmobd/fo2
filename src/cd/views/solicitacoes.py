from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import has_permission

import lotes.models

import cd.forms
import cd.models as models


class Solicitacoes(LoginRequiredMixin, View):

    def __init__(self):
        self.Form_class = cd.forms.SolicitacaoForm
        self.template_name = 'cd/solicitacoes.html'
        self.title_name = 'Solicitações de lotes'
        self.SL = lotes.models.SolicitaLote
        self.id = None

    def lista(self):
        fields = ('codigo', 'ativa', 'descricao',
                  'usuario__username', 'update_at',
                  'total_qtd', 'total_no_cd')
        descriptions = ('Código', 'Ativa para o usuário', 'Descrição',
                        'Usuário', 'Última alteração', 'Qtd. total',
                        'Qtd. do CD')
        headers = dict(zip(fields, descriptions))

        cursor_def = connection.cursor()
        data = models.solicita_lote(cursor_def)
        for row in data:
            row['codigo|LINK'] = reverse(
                'cd:solicitacao_detalhe', args=[row['id']])
        context = {
            'headers': headers,
            'fields': fields,
            'data': data,
        }
        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id:
            if self.id == 'add':
                if has_permission(request, 'lotes.add_solicitalote'):
                    context['form'] = self.Form_class()
                else:
                    context['msg_erro'] = \
                        'Usuário não tem direito de criar solicitações.'
                    self.id = None
            else:
                if has_permission(request, 'lotes.change_solicitalote'):
                    data = self.SL.objects.filter(id=self.id)
                    if len(data) == 0:
                        self.id = None
                    else:
                        row = data[0]
                        context['id'] = self.id
                        context['form'] = self.Form_class(
                            initial={'codigo': row.codigo,
                                     'descricao': row.descricao,
                                     'ativa': row.ativa})
                else:
                    context['msg_erro'] = \
                        'Usuário não tem direito de alterar solicitações.'
                    self.id = None

        if not self.id:
            context.update(self.lista())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'id' in kwargs:
            self.id = kwargs['id']

        form = self.Form_class(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            descricao = form.cleaned_data['descricao']
            ativa = form.cleaned_data['ativa']
            if ativa:
                outras_ativas = self.SL.objects.filter(
                    usuario=request.user,
                    ativa=True
                )
                if self.id != 'add':
                    outras_ativas = outras_ativas.exclude(id=self.id)
                if len(outras_ativas) != 0:
                    for soli in outras_ativas:
                        soli.ativa = False
                        soli.save()
            grava = True
            if self.id == 'add':
                try:
                    self.SL.objects.get(codigo=codigo.upper())
                    context['msg_erro'] = 'Já existe uma solicitação ' \
                        'com o código "{}".'.format(codigo)
                    grava = False
                except self.SL.DoesNotExist:
                    solicitacao = self.SL()
            else:
                solicitacao = self.SL.objects.get(id=self.id)

            if grava:
                try:
                    solicitacao.usuario = request.user
                    solicitacao.codigo = codigo
                    solicitacao.descricao = descricao
                    solicitacao.ativa = ativa
                    solicitacao.save()
                except IntegrityError as e:
                    context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                        'a solicitação. <{}>'.format(str(e))

            context.update(self.lista())
        else:
            self.context['form'] = form
        return render(request, self.template_name, context)
