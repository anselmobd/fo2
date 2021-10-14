from pprint import pprint

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection, IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission, rec_trac_log_to_dict
from geral.models import RecordTracking
from utils.functions import untuple_keys_concat
from utils.functions.digits import fo2_digit_with

import lotes.models
import lotes.queries.pedido

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

    def lista(self, filtro=None, data=None, ref=None, qtdcd=None, pagina=None):
        fields = (
            'numero', 'codigo', 'ativa', 'descricao', 'pedidos',
            'data', 'usuario__username', 'concluida', 'can_print', 'coleta',
            'update_at', 'total_qtd', 'total_no_cd'
        )
        descriptions = (
             '#número', 'Código', 'Ativa', 'Descrição', 'Pedidos',
            'Data do embarque', 'Usuário', 'Concluída', 'Imprime', 'Coleta CD',
            'Última alteração', 'Qtd. total', 'Qtd. no CD'
        )
        headers = dict(zip(fields, descriptions))

        cursor_def = connection.cursor()
        data = queries.lista_solicita_lote(cursor_def, filtro, data, ref)

        if qtdcd != 'nf':
            data = [
                row for row in data
                if (qtdcd == 'iz' and row['total_no_cd'] == 0)
                or (qtdcd == 'dz' and row['total_no_cd'] != 0)
            ]

        por_pagina = 100
        paginator = Paginator(data, por_pagina)
        try:
            data = paginator.page(pagina)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        for row in data:
            if not row['pedidos']:
                row['pedidos'] = '-'
            row['codigo|LINK'] = reverse(
                'cd:solicitacao_detalhe', args=[row['id']])
        context = {
            'headers': headers,
            'fields': fields,
            'data': data,
            'ref': ref,
            'por_pagina': por_pagina,
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

    def hidden_field(self, form, field):
        form.fields[field].widget = forms.HiddenInput()

    def ini_context(self, request):
        return {
            'titulo': self.title_name,
            'add_solicita': has_permission(
                request, 'lotes.add_solicitalote'),
            'change_solicita': has_permission(
                request, 'lotes.change_solicitalote'),
            'libera_coleta': has_permission(
                request, 'lotes.libera_coleta_de_solicitacao'),
            'reabre': has_permission(
                request, 'lotes.can_reabrir_solicitacao_completada'),
        }

    def get(self, request, *args, **kwargs):
        context = self.ini_context(request)

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id:
            if self.id == 'add':
                if has_permission(request, 'lotes.add_solicitalote'):
                    context['form'] = self.Form_class()
                    self.hidden_field(context['form'], 'concluida')
                    self.hidden_field(context['form'], 'can_print')
                    self.hidden_field(context['form'], 'coleta')
                else:
                    context['msg_erro'] = \
                        'Usuário não tem direito de criar solicitações.'
                    self.id = None
            else:
                data = self.SL.objects.filter(id=self.id)
                if len(data) == 0:
                    self.id = None
                else:

                    data_ped = lotes.models.SolicitaLotePedido.objects.filter(
                        solicitacao=self.id).order_by('pedido').values('pedido')
                    pedidos = ' '.join([
                        str(r['pedido']) for r in data_ped
                    ])

                    row = data[0]
                    dia = row.data.strftime(
                        "%Y-%m-%d") if row.data else None
                    context['id'] = self.id
                    context['form'] = self.Form_class(
                        initial={'codigo': row.codigo,
                                 'descricao': row.descricao,
                                 'pedidos': pedidos,
                                 'data': dia,
                                 'ativa': row.ativa,
                                 'concluida': row.concluida,
                                 'can_print': row.can_print,
                                 'coleta': row.coleta,
                                 })

                    context.update({
                        'echo_numero': f'#{fo2_digit_with(row.id)}',
                        'echo_id': row.id,
                    })
                    if row.concluida or not context['change_solicita']:
                        context.update({
                            'echo_codigo': row.codigo,
                            'echo_descricao': row.descricao,
                            'echo_data': row.data,
                            'echo_ativa': row.ativa,
                        })
                    if row.concluida and not context['reabre']:
                        context.update({
                            'echo_concluida': row.concluida,
                        })
                    if row.concluida and not context['libera_coleta']:
                        context.update({
                            'echo_coleta': row.coleta,
                        })

                    if row.concluida:
                        self.hidden_field(context['form'], 'codigo')
                        self.hidden_field(context['form'], 'descricao')
                        self.hidden_field(context['form'], 'data')
                        self.hidden_field(context['form'], 'ativa')
                        if not context['reabre']:
                            self.hidden_field(context['form'], 'concluida')
                        if not context['libera_coleta']:
                            self.hidden_field(context['form'], 'coleta')
                    else:
                        self.hidden_field(context['form'], 'can_print')
                        self.hidden_field(context['form'], 'coleta')

                    context.update(self.monta_hdata())

        if not self.id:
            context['filter'] = self.Filter_class()
            context.update(self.lista())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.ini_context(request)
        cursor = db_cursor_so(request)

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id is None:
            filter = self.Filter_class(request.POST)
            if filter.is_valid():
                filtro = filter.cleaned_data['filtro']
                data = filter.cleaned_data['data']
                ref = filter.cleaned_data['ref']
                qtdcd = filter.cleaned_data['qtdcd']
                pagina = filter.cleaned_data['pagina']
            else:
                filtro = None
                data = None
                ref = None
                qtdcd = None
                pagina = None
            context['filter'] = filter
            context.update(self.lista(filtro, data, ref, qtdcd, pagina))
            return render(request, self.template_name, context)

        form = self.Form_class(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            descricao = form.cleaned_data['descricao']
            pedidos = form.cleaned_data['pedidos']
            data = form.cleaned_data['data']
            concluida = form.cleaned_data['concluida']
            if concluida:
                ativa = False
                can_print = form.cleaned_data['can_print']
                coleta = form.cleaned_data['coleta']
            else:
                ativa = form.cleaned_data['ativa']
                can_print = False
                coleta = False
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
                    diferente = False
                    if solicitacao.usuario != request.user:
                        diferente = True
                        solicitacao.usuario = request.user
                    if solicitacao.codigo != codigo:
                        diferente = True
                        solicitacao.codigo = codigo
                    if solicitacao.descricao != descricao:
                        diferente = True
                        solicitacao.descricao = descricao
                    if solicitacao.data != data:
                        diferente = True
                        solicitacao.data = data
                    if solicitacao.ativa != ativa:
                        diferente = True
                        solicitacao.ativa = ativa
                    if solicitacao.concluida != concluida:
                        diferente = True
                        solicitacao.concluida = concluida
                    if solicitacao.can_print != can_print:
                        diferente = True
                        solicitacao.can_print = can_print
                    if solicitacao.coleta != coleta:
                        diferente = True
                        solicitacao.coleta = coleta
                    if diferente:
                        solicitacao.save()

                    ipedidos = []
                    for pedido in pedidos.split(' '):
                        try:
                            ipedido = int(pedido)
                            ipedidos.append(ipedido)
                        except Exception:
                            pass
                    data_ped = lotes.models.SolicitaLotePedido.objects.filter(
                        solicitacao=solicitacao)
                    ipedidos_ja_gravados = []
                    for slp in data_ped:
                        if slp.pedido not in ipedidos:
                            slp.delete()
                        else:
                            ipedidos_ja_gravados.append(slp.pedido)

                    for ipedido in ipedidos:
                        if ipedido not in ipedidos_ja_gravados:
                            ped_inf = lotes.queries.pedido.ped_inform(
                                cursor, ipedido)
                            if len(ped_inf) == 0:
                                continue
                            if ped_inf[0]['STATUS_PEDIDO'][0] == '0':
                                slp = lotes.models.SolicitaLotePedido(
                                    solicitacao=solicitacao, pedido=ipedido)
                                slp.save()

                except IntegrityError as e:
                    context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                        'a solicitação. <{}>'.format(str(e))

            context['filter'] = self.Filter_class()
            context.update(self.lista())
        else:
            context['form'] = form
        return render(request, self.template_name, context)
