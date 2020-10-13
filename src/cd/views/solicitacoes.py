from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from geral.functions import has_permission, rec_trac_log_to_dict
from geral.models import RecordTracking
from utils.functions import untuple_keys_concat

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
            'data', 'usuario__username', 'concluida', 'can_print', 'coleta',
            'update_at', 'total_qtd', 'total_no_cd'
        )
        descriptions = (
            '#número', 'Código', 'Ativa', 'Descrição',
            'Data do embarque', 'Usuário', 'Concluída', 'Imprime', 'Coleta CD',
            'Última alteração', 'Qtd. total', 'Qtd. do CD'
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

    def monta_hdata(self):
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
        row = {
            'codigo': '',
            'descricao': '',
            'data': '',
            'ativa': False,
            'concluida': False,
            'can_print': False,
            'coleta': False,
            'update_at': '',
        }
        hdata = []
        for rec in records:
            if rec.get('usuario', None):
                if isinstance(rec['usuario'], str):
                    rec['usuario__username'] = rec['usuario']
                else:
                    rec['usuario__username'] = \
                        rec['usuario'].username
            rowold = row.copy()
            row.update(rec)
            row_styles = {}
            for field in row:
                if row.get(field, '') == rowold.get(field, ''):
                    row_styles[f'{field}|STYLE'] = "color: gray"
            rowdata = row.copy()
            rowdata.update(row_styles)
            hdata.append(rowdata)
        hdata.reverse()
        icon_on = (
            '<span class="glyphicon glyphicon-ok-circle" '
            'aria-hidden="true"></span>'
        )
        style_on = 'color: lightgreen'
        icon_off = (
            '<span class="glyphicon glyphicon-remove-circle" '
            'aria-hidden="true"></span>'
        )
        style_off = 'color: red'
        for row in hdata:
            if row['codigo'] is None:
                row['codigo'] = ''
            if row['descricao'] is None:
                row['descricao'] = ''
            if row['data'] is None:
                row['data'] = '-'
            if 'ativa|STYLE' not in row:
                row['ativa|STYLE'] = style_on if row['ativa'] else style_off
            row['ativa'] = icon_on if row['ativa'] else icon_off
            if 'concluida|STYLE' not in row:
                row['concluida|STYLE'] = \
                    style_on if row['concluida'] else style_off
            row['concluida'] = icon_on if row['concluida'] else icon_off
            if 'can_print|STYLE' not in row:
                row['can_print|STYLE'] = \
                    style_on if row['can_print'] else style_off
            row['can_print'] = icon_on if row['can_print'] else icon_off
            if 'coleta|STYLE' not in row:
                row['coleta|STYLE'] = style_on if row['coleta'] else style_off
            row['coleta'] = icon_on if row['coleta'] else icon_off
        hfields = (
            'codigo', 'descricao', 'data', 'usuario__username',
            'ativa', 'concluida', 'can_print', 'coleta', 'update_at',
        )
        hheaders = (
            'Código', 'Descrição', 'Data do embarque', 'Usuário',
            'Ativa', 'Concluída', 'Imprime', 'Coleta CD', 'Última alteração',
        )
        hstyle = untuple_keys_concat({
            (5, 6, 7, 8): 'text-align: center;',
        })
        return {
            'hheaders': hheaders,
            'hfields': hfields,
            'hsafe': ['ativa', 'concluida', 'can_print', 'coleta'],
            'hstyle': hstyle,
            'hdata': hdata,
        }

    def disable_fields(self, form, fields, onoff):
        for field in form.fields:
            if field in fields:
                form.fields[field].disabled = onoff
            else:
                form.fields[field].disabled = not onoff

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
                        dia = row.data.strftime(
                            "%Y-%m-%d") if row.data else None
                        context['id'] = self.id
                        context['form'] = self.Form_class(
                            initial={'codigo': row.codigo,
                                     'descricao': row.descricao,
                                     'data': dia,
                                     'ativa': row.ativa,
                                     'concluida': row.concluida,
                                     'can_print': row.can_print,
                                     'coleta': row.coleta,
                                     })
                        self.disable_fields(
                            context['form'],
                            ['can_print', 'coleta'],
                            not row.concluida,
                        )
                        context.update(self.monta_hdata())
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
            concluida = form.cleaned_data['concluida']
            can_print = form.cleaned_data['can_print']
            coleta = form.cleaned_data['coleta']
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
                    solicitacao.concluida = concluida
                    solicitacao.can_print = can_print
                    solicitacao.coleta = coleta
                    solicitacao.save()
                except IntegrityError as e:
                    context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                        'a solicitação. <{}>'.format(str(e))

            context['filter'] = self.Filter_class()
            context.update(self.lista())
        else:
            self.context['form'] = form
        return render(request, self.template_name, context)
