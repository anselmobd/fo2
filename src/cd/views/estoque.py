from pprint import pprint
from datetime import timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections
from django.db.models import Sum
from django.shortcuts import render
from django.views import View
from django.urls import reverse

import lotes.models
import lotes.queries.op
from geral.functions import request_user
import produto.queries

import cd.forms


class Estoque(View):

    def __init__(self):
        self.Form_class = cd.forms.EstoqueForm
        self.template_name = 'cd/estoque.html'
        self.title_name = 'Estoque'

    def mount_context(self, form, user):
        cursor = connections['so'].cursor()
        linhas_pagina = 100
        page = form.cleaned_data['page']

        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        op = form.cleaned_data['op']
        ref = form.cleaned_data['ref']
        tam = form.cleaned_data['tam']
        cor = form.cleaned_data['cor']
        data_de = form.cleaned_data['data_de']
        data_ate = form.cleaned_data['data_ate']
        if not data_ate:
            data_ate = data_de
        ordem = form.cleaned_data['ordem']

        context = {'endereco': endereco,
                   'lote': lote,
                   'op': op,
                   'ref': ref,
                   'tam': tam,
                   'cor': cor,
                   'ordem': ordem,
                   'data_de': data_de,
                   'data_ate': data_ate,
                   'linhas_pagina': linhas_pagina,
                   }

        if data_ate:
            data_ate = data_ate + timedelta(days=1)
        data_rec = lotes.models.Lote.objects
        if endereco:
            data_rec = data_rec.filter(local=endereco)
        else:
            # data_rec = data_rec.filter(local__isnull=False)
            data_rec = data_rec.exclude(
                local__isnull=True
            ).exclude(
                local__exact='')
        if lote:
            data_rec = data_rec.filter(lote=lote)
        if op:
            data_rec = data_rec.filter(op=op)
        if ref:
            data_rec = data_rec.filter(referencia=ref)
        if tam:
            data_rec = data_rec.filter(tamanho=tam)
        if cor:
            data_rec = data_rec.filter(cor=cor)
        if data_de:
            data_rec = data_rec.filter(local_at__gte=data_de)
            data_rec = data_rec.filter(local_at__lte=data_ate)

        title_ref = (
            'Referência<span '
            'style="font-size: 50%;vertical-align: super;" '
            'class="glyphicon glyphicon-comment" '
            'aria-hidden="true"></span>'
        )
        if ordem == 'B':  # Hora de bipagem
            data_rec = data_rec.order_by('-local_at')
            headers = [
                'Em', 'Por', 'Endereço', 'Lote',
                (title_ref, ), 'Tamanho', 'Cor', 'Qtd.Ori.', 'OP', 'Pedido',
                'Estágio', 'Alter.', 'Qtd.', 'Q.Livre', 'Q.End.']
            fields = [
                'local_at', 'local_usuario__username', 'local', 'lote',
                'referencia', 'tamanho', 'cor', 'qtd_produzir', 'op', 'pedido',
                'estagio', 'qtd_dif', 'qtd_est', 'qtd', 'conserto']
        elif ordem == 'O':  # OP Referência Cor Tamanho Endereço Lote
            data_rec = data_rec.order_by(
                'op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote')
            headers = [
                'OP', 'Pedido', (title_ref, ), 'Tamanho', 'Cor', 'Qtd.Ori.',
                'Estágio', 'Alter.', 'Qtd.', 'Q.Livre',
                'Q.End.', 'Endereço', 'Lote', 'Em',
                'Por']
            fields = [
                'op', 'pedido', 'referencia', 'tamanho', 'cor', 'qtd_produzir',
                'estagio', 'qtd_dif', 'qtd_est', 'qtd',
                'conserto', 'local', 'lote', 'local_at',
                'local_usuario__username']
        elif ordem == 'R':  # Referência Cor Tamanho Endereço OP Lote
            data_rec = data_rec.order_by(
                'referencia', 'cor', 'ordem_tamanho', 'local', 'op', 'lote')
            headers = [
                (title_ref, ), 'Tamanho', 'Cor', 'Qtd.Ori.',
                'Estágio', 'Alter.', 'Qtd.', 'Q.Livre',
                'Q.End.', 'Endereço', 'OP', 'Pedido',
                'Lote', 'Em', 'Por']
            fields = [
                'referencia', 'tamanho', 'cor', 'qtd_produzir',
                'estagio', 'qtd_dif', 'qtd_est', 'qtd',
                'conserto', 'local', 'op', 'pedido',
                'lote', 'local_at', 'local_usuario__username']
        else:  # E: Endereço OP Referência Cor Tamanho Lote
            data_rec = data_rec.order_by(
                'local', 'op', 'referencia', 'cor', 'ordem_tamanho', 'lote')
            headers = [
                'Endereço', 'OP', 'Pedido', (title_ref, ), 'Tamanho', 'Cor',
                'Qtd.Ori.', 'Estágio', 'Alter.', 'Qtd.', 'Q.Livre',
                'Q.End.', 'Lote', 'Em', 'Por']
            fields = [
                'local', 'op', 'pedido', 'referencia', 'tamanho', 'cor',
                'qtd_produzir', 'estagio', 'qtd_dif', 'qtd_est', 'qtd',
                'conserto', 'lote', 'local_at', 'local_usuario__username']

        data = data_rec.values(
            'local', 'local_at', 'local_usuario__username', 'op', 'lote',
            'referencia', 'tamanho', 'cor', 'qtd_produzir', 'qtd', 'estagio',
            'create_at', 'update_at', 'conserto')

        quant_lotes = len(data)
        paginator = Paginator(data, linhas_pagina)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        if len(data) != 0:
            ops = set()
            ref_list = set()
            for row in data:
                ops.add(row['op'])
                ref_list.add(row['referencia'])

            ref_data = produto.queries.ref_inform(cursor, tuple(ref_list))
            ref_dict = {r['REF']: r for r in ref_data}

            ops_info = lotes.queries.op.busca_ops_info(cursor, ops)
            ops_dict = {o['op']: o for o in ops_info}

        solicit_cod = None
        solicit_recs = lotes.models.SolicitaLote.objects.filter(
            usuario=user, ativa=True)
        if len(solicit_recs) == 1:
            solicit_cod = solicit_recs[0].codigo
            solicit_id = solicit_recs[0].id
            context['solicit_cod'] = solicit_cod
            context['solicit_id'] = solicit_id

        headers.append('Solicitar')
        fields.append('solicita')

        for row in data:
            row['referencia|HOVER'] = ref_dict[row['referencia']]['DESCR']
            row['qtd_est'] = row['qtd'] + row['conserto']
            row['pedido'] = ops_dict[row['op']]['pedido']
            if row['pedido'] == 0:
                row['pedido'] = '-'
            else:
                row['pedido|LINK'] = reverse(
                    'producao:pedido__get', args=[row['pedido']])
            if row['qtd']:
                if row['update_at'] is None:
                    row['update_at'] = row['create_at']
                slq = lotes.models.SolicitaLoteQtd.objects.filter(
                    lote__lote=row['lote'],  # update_at__gte=row['update_at']
                    ).aggregate(Sum('qtd'))
                slq_qtd = 0
                if slq:
                    if slq['qtd__sum']:
                        slq_qtd = slq['qtd__sum']

                if solicit_cod and (row['qtd'] - slq_qtd) > 0:
                    row['solicita'] = '''
                        <a title="Solicitação parcial de lote"
                         href="javascript:void(0);"
                         onclick="solicita_lote(
                            \'{lote}\', \'{ref}\', \'{cor}\', \'{tam}\',
                            \'{qtd_resta}\', \'{solicit_cod}\',
                            \'{solicit_id}\', \'{qtd_limite}\', \'N\');"
                        ><span
                        class="glyphicon glyphicon-triangle-bottom"
                        aria-hidden="true"></span></a>
                        &nbsp;
                        <span id="qtd_resta_{lote}">{qtd_resta}</span>
                        &nbsp;
                        <a class="solicitacao_inteira_de_lote"
                         title="Solicitação inteira de lote"
                         href="javascript:void(0);"
                         onclick="solicita_lote(
                            \'{lote}\', \'{ref}\', \'{cor}\', \'{tam}\',
                            \'{qtd_resta}\', \'{solicit_cod}\',
                            \'{solicit_id}\', \'{qtd_limite}\', \'S\');"
                        ><span
                        class="glyphicon glyphicon-unchecked"
                        aria-hidden="true"></span></a>
                    '''.format(
                        lote=row['lote'],
                        ref=row['referencia'],
                        cor=row['cor'],
                        tam=row['tamanho'],
                        qtd_resta=row['qtd'] - slq_qtd,
                        solicit_cod=solicit_cod,
                        solicit_id=solicit_id,
                        qtd_limite=row['qtd'])
                else:
                    row['solicita'] = row['qtd'] - slq_qtd
            else:
                row['solicita'] = '0'
            row['op|LINK'] = reverse(
                'producao:op__get', args=[row['op']])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])
            if row['estagio'] == 999:
                row['estagio'] = 'Finalizado'
            if row['qtd'] == row['qtd_produzir']:
                row['qtd_dif'] = ''
            else:
                row['qtd_dif'] = '*'

        context.update({
            'safe': ['solicita'],
            'headers': headers,
            'fields': fields,
            'data': data,
            'quant_lotes': quant_lotes,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'ordem' in kwargs:
            if kwargs['ordem'] == 'B':  # Hora de bipagem
                kwargs['endereco'] = kwargs['filtro']
            # OP Referência Cor Tamanho Endereço Lote
            elif kwargs['ordem'] == 'O':
                kwargs['op'] = kwargs['filtro']
            # Referência Cor Tamanho Endereço OP Lote
            elif kwargs['ordem'] == 'R':
                kwargs['ref'] = kwargs['filtro']
            else:  # E: Endereço OP Referência Cor Tamanho Lote
                kwargs['endereco'] = kwargs['filtro']
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ordem' in kwargs:
            form.data['ordem'] = kwargs['ordem']
            if 'endereco' in kwargs:
                form.data['endereco'] = kwargs['endereco']
            if 'op' in kwargs:
                form.data['op'] = kwargs['op']
            if 'ref' in kwargs:
                form.data['ref'] = kwargs['ref']
        if form.is_valid():
            user = request_user(request)
            data = self.mount_context(form, user)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
