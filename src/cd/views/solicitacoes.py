from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import has_permission, rec_trac_log_to_dict
from geral.models import RecordTracking

import lotes.models

import cd.forms
import cd.queries as queries


class Solicitacoes(LoginRequiredMixin, View):

    def __init__(self):
        self.Form_class = cd.forms.SolicitacaoForm
        self.Filter_class = cd.forms.FiltraSolicitacaoForm
        self.template_name = 'cd/solicitacoes.html'
        self.title_name = 'Solicitações de lotes'
        self.SL = lotes.models.SolicitaLote
        self.id = None

    def lista(self, filtro=None, data=None, ref=None):
        fields = (
            'numero', 'codigo', 'ativa', 'descricao',
            'data', 'usuario__username', 'update_at',
            'total_qtd', 'total_no_cd'
        )
        descriptions = (
            '#número', 'Código', 'Ativa para o usuário', 'Descrição',
            'Data do embarque', 'Usuário', 'Última alteração',
            'Qtd. total', 'Qtd. do CD'
        )
        headers = dict(zip(fields, descriptions))

        cursor_def = connection.cursor()
        data = queries.lista_solicita_lote(cursor_def, filtro, data, ref)
        for row in data:
            row['codigo|LINK'] = reverse(
                'cd:solicitacao_detalhe', args=[row['id']])
        context = {
            'headers': headers,
            'fields': fields,
            'data': data,
            'ref': ref,
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
                                     'data': row.data,
                                     'ativa': row.ativa,
                                     'can_print': row.can_print,
                                     })
                        rec_trac = RecordTracking.objects.filter(
                            table='SolicitaLote',
                            record_id=self.id).values(
                            'log', 'log_version').order_by(
                            'time'
                            )
                        records = [
                            rec_trac_log_to_dict(
                                rec['log'], rec['log_version'])
                            for rec in list(rec_trac)
                        ]
                        row = {}
                        hdata = []
                        for rec in records:
                            if rec.get('usuario', None):
                                if isinstance(rec['usuario'], str):
                                    rec['usuario__username'] = rec['usuario']
                                else:
                                    rec['usuario__username'] = \
                                        rec['usuario'].username
                            row.update(rec)
                            hdata.append(row.copy())
                        hdata.reverse()
                        for row in hdata:
                            if row['codigo'] is None:
                                row['codigo'] = ''
                            if row['descricao'] is None:
                                row['descricao'] = ''
                            if row['data'] is None:
                                row['data'] = '-'
                        hfields = (
                            'codigo', 'ativa', 'descricao',
                            'data', 'usuario__username', 'update_at',
                        )
                        hheaders = (
                            'Código', 'Ativa para o usuário', 'Descrição',
                            'Data do embarque', 'Usuário',
                            'Última alteração',
                        )
                        context.update({
                            'hheaders': hheaders,
                            'hfields': hfields,
                            'hdata': hdata,
                        })
                else:
                    context['msg_erro'] = \
                        'Usuário não tem direito de alterar solicitações.'
                    self.id = None

        if not self.id:
            context['filter'] = self.Filter_class()
            context.update(self.lista())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id is None:
            filter = self.Filter_class(request.POST)
            if filter.is_valid():
                filtro = filter.cleaned_data['filtro']
                data = filter.cleaned_data['data']
                ref = filter.cleaned_data['ref']
            else:
                filtro = None
                data = None
                ref = None
            context['filter'] = filter
            context.update(self.lista(filtro, data, ref))
            return render(request, self.template_name, context)

        form = self.Form_class(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            descricao = form.cleaned_data['descricao']
            data = form.cleaned_data['data']
            ativa = form.cleaned_data['ativa']
            can_print = form.cleaned_data['can_print']
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
                    solicitacao.data = data
                    solicitacao.ativa = ativa
                    solicitacao.can_print = can_print
                    solicitacao.save()
                except IntegrityError as e:
                    context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                        'a solicitação. <{}>'.format(str(e))

            context['filter'] = self.Filter_class()
            context.update(self.lista())
        else:
            self.context['form'] = form
        return render(request, self.template_name, context)
