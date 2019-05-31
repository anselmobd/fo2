from pprint import pprint
import re
import datetime
from datetime import timedelta
from pytz import utc

from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.mixins \
    import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User

from fo2.models import rows_to_dict_list_lower, GradeQtd
from fo2.template import group_rowspan

from utils.views import totalize_grouped_data
import lotes.models
from geral.functions import request_user, has_permission

import cd.models as models
import cd.forms


def index(request):
    context = {}
    return render(request, 'cd/index.html', context)


def teste_som(request):
    context = {}
    return render(request, 'cd/teste_som.html', context)


class LotelLocal(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.LoteForm
        self.template_name = 'cd/lote_local.html'
        self.title_name = 'Inventariar'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]
        identificado = form.cleaned_data['identificado']

        if endereco == 'SAI':
            endereco = None

        context = {'endereco': endereco}

        lote_sys = lotes.models.posicao_get_item(
            cursor, periodo, ordem_confeccao)
        if len(lote_sys) == 0:
            if endereco is not None:
                context.update({
                    'erro': 'Lote não encontrado no Systêxtil. Única ação '
                            'possivel é dar saída (Endereço "SAI").'})
                return context

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        if lote_rec.referencia >= 'C0000':
            if endereco is not None:
                context.update({
                    'erro': 'Lote de MD. Única ação '
                            'possivel é dar saída (Endereço "SAI").'})
                return context

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': lote_rec.local,
            })

        if len(lote_sys) != 0:
            try:
                lote_rec_estag = lotes.models.Lote.objects.filter(
                    Q(estagio=63) | Q(estagio=66) |
                    Q(estagio=999)).get(lote=lote)
            except lotes.models.Lote.DoesNotExist:
                context.update({
                    'erroestagio': '63, 66 ou finalizado',
                    'estagio': lote_rec.estagio,
                    })
                return context

        if identificado:
            form.data['identificado'] = None
            form.data['lote'] = None
            if lote != identificado:
                context.update({
                    'erro': 'A confirmação é bipando o mesmo lote. '
                            'Identifique o lote novamente.'})
                return context

            lote_rec.local = endereco
            lote_rec.local_usuario = request.user
            lote_rec.save()

            context['identificado'] = identificado
        else:
            context['lote'] = lote
            if lote_rec.local != endereco:
                context['confirma'] = True
                form.data['identificado'] = form.data['lote']
            form.data['lote'] = None

        if not endereco:
            return context

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco).order_by(
                '-local_at'
                ).values(
                    'op', 'lote', 'qtd_produzir',
                    'referencia', 'cor', 'tamanho',
                    'local_at', 'local_usuario__username')
        if lotes_no_local:
            q_itens = 0
            for row in lotes_no_local:
                q_itens += row['qtd_produzir']
            context.update({
                'q_lotes': len(lotes_no_local),
                'q_itens': q_itens,
                'headers': ('Bipado em', 'Bipado por',
                            'Lote', 'Quant.',
                            'Ref.', 'Cor', 'Tam.', 'OP'),
                'fields': ('local_at', 'local_usuario__username',
                           'lote', 'qtd_produzir',
                           'referencia', 'cor', 'tamanho', 'op'),
                'data': lotes_no_local,
                })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class TrocaLocal(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_relocate_lote'
        self.Form_class = cd.forms.TrocaLocalForm
        self.template_name = 'cd/troca_local.html'
        self.title_name = 'Trocal endereço'

    def mount_context(self, request, form):
        endereco_de = form.cleaned_data['endereco_de']
        endereco_para = form.cleaned_data['endereco_para']

        context = {'endereco_de': endereco_de,
                   'endereco_para': endereco_para}

        lotes_de = lotes.models.Lote.objects.filter(local=endereco_de)
        if len(lotes_de) == 0:
            context.update({'erro': 'Endereço antigo está vazio'})
            return context

        lotes_para = lotes.models.Lote.objects.filter(local=endereco_para)
        if len(lotes_para) != 0:
            context.update({'erro': 'Endereço novo NÃO está vazio'})
            return context

        if request.POST.get("troca"):
            context.update({'confirma': True})
            busca_endereco = endereco_de

        else:
            lotes_recs = lotes.models.Lote.objects.filter(local=endereco_de)
            for lote in lotes_recs:
                lote.local = endereco_para
                lote.local_usuario = request.user
                lote.save()
            form.data['endereco_de'] = None
            form.data['endereco_para'] = None
            busca_endereco = endereco_para

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=busca_endereco).order_by(
                'referencia', 'cor', 'ordem_tamanho', 'op', 'lote'
                ).values(
                    'op', 'lote', 'qtd_produzir',
                    'referencia', 'cor', 'tamanho',
                    'local_at', 'local_usuario__username')
        q_itens = 0
        for row in lotes_no_local:
            q_itens += row['qtd_produzir']
        context.update({
            'q_lotes': len(lotes_no_local),
            'q_itens': q_itens,
            'headers': ('Referência', 'Tamanho', 'Cor', 'Quant',
                        'OP', 'Lote', 'Em',
                        'Por'),
            'fields': ('referencia', 'tamanho', 'cor', 'qtd_produzir',
                       'op', 'lote', 'local_at',
                       'local_usuario__username'),
            'data': lotes_no_local,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


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

        if ordem == 'B':  # Hora de bipagem
            data_rec = data_rec.order_by('-local_at')
            headers = [
                'Em', 'Por', 'Endereço', 'Lote',
                'Referência', 'Tamanho', 'Cor', 'Qtd.Ori.', 'OP', 'Pedido',
                'Estágio', 'Alter.', 'Qtd.']
            fields = [
                'local_at', 'local_usuario__username', 'local', 'lote',
                'referencia', 'tamanho', 'cor', 'qtd_produzir', 'op', 'pedido',
                'estagio', 'qtd_dif', 'qtd']
        elif ordem == 'O':  # OP Referência Cor Tamanho Endereço Lote
            data_rec = data_rec.order_by(
                'op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote')
            headers = [
                'OP', 'Pedido', 'Referência', 'Tamanho', 'Cor', 'Qtd.Ori.',
                'Estágio', 'Alter.', 'Qtd.', 'Endereço', 'Lote', 'Em',
                'Por']
            fields = [
                'op', 'pedido', 'referencia', 'tamanho', 'cor', 'qtd_produzir',
                'estagio', 'qtd_dif', 'qtd', 'local', 'lote', 'local_at',
                'local_usuario__username']
        elif ordem == 'R':  # Referência Cor Tamanho Endereço OP Lote
            data_rec = data_rec.order_by(
                'referencia', 'cor', 'ordem_tamanho', 'local', 'op', 'lote')
            headers = [
                'Referência', 'Tamanho', 'Cor', 'Qtd.Ori.',
                'Estágio', 'Alter.', 'Qtd.', 'Endereço', 'OP', 'Pedido',
                'Lote', 'Em', 'Por']
            fields = [
                'referencia', 'tamanho', 'cor', 'qtd_produzir',
                'estagio', 'qtd_dif', 'qtd', 'local', 'op', 'pedido',
                'lote', 'local_at', 'local_usuario__username']
        else:  # E: Endereço OP Referência Cor Tamanho Lote
            data_rec = data_rec.order_by(
                'local', 'op', 'referencia', 'cor', 'ordem_tamanho', 'lote')
            headers = [
                'Endereço', 'OP', 'Pedido', 'Referência', 'Tamanho', 'Cor',
                'Qtd.Ori.', 'Estágio', 'Alter.', 'Qtd.', 'Lote',
                'Em', 'Por']
            fields = [
                'local', 'op', 'pedido', 'referencia', 'tamanho', 'cor',
                'qtd_produzir', 'estagio', 'qtd_dif', 'qtd', 'lote',
                'local_at', 'local_usuario__username']

        data = data_rec.values(
            'local', 'local_at', 'local_usuario__username', 'op', 'lote',
            'referencia', 'tamanho', 'cor', 'qtd_produzir', 'qtd', 'estagio',
            'create_at', 'update_at')

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
            for row in data:
                ops.add(row['op'])
            ops_info = lotes.models.busca_ops_info(cursor, ops)
            for row in ops_info:
                if row['pedido'] == 0:
                    row['pedido'] = '-'

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
            row['pedido'] = [op_info for op_info in ops_info
                             if op_info['op'] == row['op']
                             ][0]['pedido']
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


class Inconsistencias(View):

    def __init__(self):
        self.template_name = 'cd/inconsist.html'
        self.title_name = 'Inconsistências Systêxtil'

    def mount_context(self, cursor, ordem, opini):
        step = 10
        data_size = 20
        context = {
            'data_size': data_size,
            'opini': opini,
            'ordem': ordem,
        }

        data = []
        for i in range(0, 999999999, step):
            ops = lotes.models.Lote.objects
            if ordem == 'A':
                ops = ops.filter(
                        op__gt=opini
                    )
            else:
                if opini == -1:
                    ops = ops.filter(
                            op__lte=999999999
                        )
                else:
                    ops = ops.filter(
                            op__lt=opini
                        )
            ops = ops.exclude(
                    local__isnull=True
                ).exclude(
                    local__exact=''
                ).values('op').distinct()
            if ordem == 'A':
                ops = ops.order_by('op')
            else:  # if ordem == 'D':
                ops = ops.order_by('-op')
            ops = ops[i:i+step]
            if len(ops) == 0:
                break

            filtro = ''
            filtro_sep = ''
            for op in ops:
                lotes_recs = lotes.models.Lote.objects.filter(
                        op=op['op']
                    ).exclude(
                        local__isnull=True
                    ).exclude(
                        local__exact='').values('lote').distinct()

                ocs = ''
                sep = ''
                for lote in lotes_recs:
                    ocs += sep + lote['lote'][4:].strip('0')
                    sep = ','

                op_ocs = '( op.ORDEM_PRODUCAO = {} ' \
                    'AND le63.ORDEM_CONFECCAO in ({}) )'.format(op['op'], ocs)
                op['oc'] = op_ocs

                filtro += filtro_sep + op_ocs
                filtro_sep = ' OR '

            sql = '''
                SELECT
                  op.ORDEM_PRODUCAO OP
                , op.SITUACAO
                , le.SEQUENCIA_ESTAGIO SEQ
                , le.CODIGO_ESTAGIO EST
                , le63.SEQUENCIA_ESTAGIO SEQ63
                , sum(le.QTDE_EM_PRODUCAO_PACOTE) QTD
                FROM PCPC_020 op -- OP capa
                LEFT JOIN PCPC_040 le63 -- lote estágio 63
                  ON le63.ordem_producao = op.ORDEM_PRODUCAO
                 AND le63.CODIGO_ESTAGIO = 63
                LEFT JOIN PCPC_040 le -- lote estágio atual
                  ON le.ordem_producao = op.ORDEM_PRODUCAO
                 AND le.PERIODO_PRODUCAO = le63.PERIODO_PRODUCAO
                 AND le.ORDEM_CONFECCAO = le63.ORDEM_CONFECCAO
                 AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                WHERE 1=1
                  -- AND op.SITUACAO <> 9 -- op.COD_CANCELAMENTO = 0
                  AND ({filtro})
                GROUP BY
                  op.ORDEM_PRODUCAO
                , op.SITUACAO
                , le.SEQUENCIA_ESTAGIO
                , le.CODIGO_ESTAGIO
                , le63.SEQUENCIA_ESTAGIO
                ORDER BY
                  op.ORDEM_PRODUCAO
                , le.SEQUENCIA_ESTAGIO
            '''.format(filtro=filtro)
            cursor.execute(sql)
            estagios = rows_to_dict_list_lower(cursor)

            for op in ops:
                row = {}
                sep = ''
                row['op'] = op['op']
                row['op|LINK'] = reverse(
                    'cd:inconsist_detalhe_op', args=[op['op']])
                row['op|TARGET'] = '_blank'
                row['cr'] = ''
                estagios_op = [r for r in estagios if r['op'] == op['op']]
                if len(estagios_op) == 0:
                    row['cr'] = 'OP sem estágio 63'
                else:
                    for estagio_op in estagios_op:
                        if estagio_op['situacao'] == 9:
                            row['cr'] += sep + 'OP Cancelada'
                        elif estagio_op['est'] is None:
                            row['cr'] += sep + 'Finalizados'
                        elif estagio_op['est'] == 63:
                            row['cr'] += sep + 'OK no 63'
                        else:
                            if estagio_op['seq'] < estagio_op['seq63']:
                                row['cr'] += sep + 'Atrasados no {}'.format(
                                    estagio_op['est'])
                            else:
                                row['cr'] += sep + 'Adiantados no {}'.format(
                                    estagio_op['est'])
                        sep = ', '
                if row['cr'] != 'OK no 63':
                    data.append(row)
            if len(data) >= data_size:
                break

        if len(data) >= data_size:
            context.update({'opnext': data[data_size-1]['op']})
        context.update({
            'headers': ['OP', 'Crítica dos lotes'],
            'fields': ['op', 'cr'],
            'data': data[:data_size],
        })
        return context

    def get(self, request, *args, **kwargs):
        if 'opini' in kwargs:
            opini = int(kwargs['opini'])
        else:
            opini = -1

        if 'ordem' in kwargs:
            ordem = kwargs['ordem']
        else:
            ordem = 'A'
        if len(ordem) == 2:
            if ordem[1] == '-':
                if ordem[0] == 'A':
                    ordem = 'D'
                else:
                    ordem = 'A'

        context = {'titulo': self.title_name}
        # form = self.Form_class()
        # context['form'] = form
        cursor = connections['so'].cursor()
        data = self.mount_context(cursor, ordem, opini)
        context.update(data)
        return render(request, self.template_name, context)


class Mapa(View):

    def __init__(self):
        self.template_name = 'cd/mapa.html'
        self.title_name = 'Mapa'

    def mount_context(self):
        enderecos = {}
        letras = [
            {'letra': 'A', 'int_ini': 1},
            {'letra': 'A', 'int_ini': 29},
            {'letra': 'A', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'B', 'int_ini': 57},
            {'letra': 'B', 'int_ini': 29},
            {'letra': 'B', 'int_ini': 1},
            {'letra': 'l'},
            {'letra': 'C', 'int_ini': 1},
            {'letra': 'C', 'int_ini': 29},
            {'letra': 'C', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'l'},
            {'letra': 'D', 'int_ini': 1},
            {'letra': 'D', 'int_ini': 29},
            {'letra': 'D', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'E', 'int_ini': 57},
            {'letra': 'E', 'int_ini': 29},
            {'letra': 'E', 'int_ini': 1},
            {'letra': 'l'},
            {'letra': 'F', 'int_ini': 1},
            {'letra': 'F', 'int_ini': 29},
            {'letra': 'F', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'G', 'int_ini': 57},
            {'letra': 'G', 'int_ini': 29},
            {'letra': 'G', 'int_ini': 1},
        ]
        for num, letra in enumerate(letras):
            ends_linha = []
            for int_end in range(28):
                if letra['letra'] == 'r':
                    conteudo = ''
                elif letra['letra'] == 'l':
                    conteudo = '==='
                else:
                    conteudo = '{}{}'.format(
                        letra['letra'], letra['int_ini']+27-int_end)
                ends_linha.append(conteudo)
            enderecos[num] = ends_linha
        context = {
            'linhas': [
                'A3º', 'A2º', 'A1º', 'rua A/B', 'B1º', 'B2º', 'B3º', '===',
                'C3º', 'C2º', 'C1º', 'rua C', '===',
                'D3º', 'D2º', 'D1º', 'rua D/E', 'E1º', 'E2º', 'E3º', '===',
                'F3º', 'F2º', 'F1º', 'rua F/G', 'G1º', 'G2º', 'G3º'
                ],
            'enderecos': enderecos,
            }

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)


class Conferencia(View):

    def __init__(self):
        self.template_name = 'cd/conferencia.html'
        self.title_name = 'Conferência detalhada'

    def mount_context(self):
        context = {}
        locais_recs = lotes.models.Lote.objects.all().exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local', 'op', 'referencia', 'cor', 'tamanho').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local', 'op', 'referencia', 'cor', 'ordem_tamanho')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'op', 'referencia', 'cor', 'tamanho', 'qlotes', 'qtdsum'))

        group = ['local']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['qlotes', 'qtdsum'],
            'count': [],
            'descr': {'op': 'Totais:'}
        })
        group_rowspan(data, group)

        headers = ['Endereço', 'OP', 'Lotes', 'Qtd.',
                   'Referência', 'Cor', 'Tamanho']
        fields = ['local', 'op', 'qlotes', 'qtdsum',
                  'referencia', 'cor', 'tamanho']

        context.update({
            'headers': headers,
            'fields': fields,
            'group': group,
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)


class ConferenciaSimples(View):

    def __init__(self):
        self.template_name = 'cd/conferencia.html'
        self.title_name = 'Conferência Simples'

    def mount_context(self):
        context = {'simples': 's'}
        locais_recs = lotes.models.Lote.objects.all().exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'qlotes', 'qtdsum'))

        headers = ['Endereço', 'Lotes (caixas)', 'Qtd. peças']
        fields = ['local', 'qlotes', 'qtdsum']

        total = data[0].copy()
        total['local'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fileds = ['qlotes', 'qtdsum']
        for field in quant_fileds:
            total[field] = 0
        for row in data:
            for field in quant_fileds:
                total[field] += row[field]
        data.append(total)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)


class InconsistenciasDetalhe(View):

    def __init__(self):
        self.template_name = 'cd/inconsist_detalhe.html'
        self.title_name = 'Detalhe de inconsistência'

    def mount_context(self, cursor, op):
        context = {'op': op}

        lotes_recs = lotes.models.Lote.objects.filter(
            op=op
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('lote').distinct()
        if len(lotes_recs) == 0:
            return context

        ocs = []
        for lote in lotes_recs:
            ocs.append(lote['lote'][4:].strip('0'))

        headers = ['Estágio', 'Lote', 'Referência', 'Cor', 'Tamanho',
                   'Quantidade']
        fields = ['est', 'lote', 'ref', 'cor', 'tam', 'qtd']

        data = models.inconsistencias_detalhe(cursor, op, ocs)

        for row in data:
            if row['seq'] == 99:
                row['est'] = 'Finalizado'
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        data63 = models.inconsistencias_detalhe(cursor, op, ocs, est63=True)

        for row in data63:
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers63': headers,
            'fields63': fields,
            'data63': data63,
        })

        return context

    def get(self, request, *args, **kwargs):
        op = int(kwargs['op'])

        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        data = self.mount_context(cursor, op)
        context.update(data)
        return render(request, self.template_name, context)


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
            if self.id == 'add':
                solicitacao = self.SL()
            else:
                solicitacao = self.SL.objects.get(id=self.id)
            solicitacao.usuario = request.user
            solicitacao.codigo = codigo
            solicitacao.descricao = descricao
            solicitacao.ativa = ativa
            solicitacao.save()

            context.update(self.lista())
        else:
            self.context['form'] = form
        return render(request, self.template_name, context)


def solicita_lote(request, solicitacao_id, lote, qtd):
    data = {}

    try:
        solicitacao = lotes.models.SolicitaLote.objects.get(
            id=solicitacao_id)
    except lotes.models.SolicitaLote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Solicitação não encontrada por id',
        })
        return JsonResponse(data, safe=False)

    try:
        lote_rec = lotes.models.Lote.objects.get(lote=lote)
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Lote não encontrado',
        })
        return JsonResponse(data, safe=False)

    try:
        iqtd = int(qtd)
    except ValueError:
        iqtd = -1
    if iqtd < 1 or iqtd > lote_rec.qtd:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Quantidade inválida',
        })
        return JsonResponse(data, safe=False)

    try:
        solicita = lotes.models.SolicitaLoteQtd()
        solicita.solicitacao = solicitacao
        solicita.lote = lote_rec
        solicita.qtd = iqtd
        solicita.save()
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro':
                'Erro ao criar registro de quantidade solicitada',
        })
        return JsonResponse(data, safe=False)

    data = {
        'result': 'OK',
        'solicitacao_id': solicitacao_id,
        'lote': lote,
        'qtd': iqtd,
        'solicita_qtd_id': solicita.id,
    }
    return JsonResponse(data, safe=False)


class SolicitacaoDetalhe(LoginRequiredMixin, View):

    def __init__(self):
        self.template_name = 'cd/solicitacao_detalhe.html'
        self.title_name = 'Detalhes de solicitação'

    def mount_context(self, solicit_id, user):
        context = {'user': user}

        try:
            solicitacao = lotes.models.SolicitaLote.objects.get(
                id=solicit_id)
        except lotes.models.SolicitaLote.DoesNotExist:
            context['erro'] = \
                'Id de solicitação inválido.'
            return context

        context['solicitacao'] = solicitacao

        solicit_qtds = lotes.models.SolicitaLoteQtd.objects.values(
            'id', 'lote__op', 'lote__lote', 'lote__referencia',
            'lote__cor', 'lote__tamanho', 'qtd', 'update_at'
        ).annotate(
            lote__local=Coalesce('lote__local', Value('-ausente-'))
        ).filter(
            solicitacao=solicitacao
        ).order_by(
            '-update_at'
        )

        for row in solicit_qtds:
            link = reverse(
                'cd:solicitacao_detalhe__get3',
                args=[solicitacao.id, 'd', row['id']])
            row['delete'] = '''
                <a title="Exclui lote"
                href="{link}"
                ><span class="glyphicon glyphicon-remove"
                aria-hidden="true"></span></a>
            '''.format(link=link)
        link = reverse(
            'cd:solicitacao_detalhe__get2',
            args=[solicitacao.id, 'l'])
        limpa = '''
            <a title="Limpa solicitação"
            href="{link}"
            ><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"
            ></span></a>
        '''.format(link=link)

        context.update({
            'safe': ['delete'],
            'headers': ['Endereço', 'OP', 'Lote', 'Referência',
                        'Cor', 'Tamanho', 'Quant. Solicitada', 'Em', (limpa,)],
            'fields': ['lote__local', 'lote__op', 'lote__lote',
                       'lote__referencia', 'lote__cor', 'lote__tamanho', 'qtd',
                       'update_at', 'delete'],
            'data': solicit_qtds,
        })

        por_endereco = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__referencia', 'lote__cor', 'lote__tamanho'
        ).annotate(
            lote__local=Coalesce('lote__local', Value('-ausente-')),
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao
        ).order_by(
            'lote__local', 'lote__op', 'lote__referencia', 'lote__cor',
            'lote__tamanho', 'lote__lote'
        )

        for lote in por_endereco:
            if lote['qtdsum'] == lote['lote__qtd_produzir']:
                lote['inteira_parcial'] = 'Lote inteiro'
            else:
                lote['inteira_parcial'] = 'Parcial'

        context.update({
            'e_headers': ['Endereço', 'OP', 'Lote',
                          'Referência', 'Cor', 'Tamanho',
                          'Quant. Solicitada', 'Solicitação'],
            'e_fields': ['lote__local', 'lote__op', 'lote__lote',
                         'lote__referencia', 'lote__cor', 'lote__tamanho',
                         'qtdsum', 'inteira_parcial'],
            'e_data': por_endereco,
        })

        referencias = lotes.models.SolicitaLoteQtd.objects.filter(
            solicitacao=solicitacao
        ).values('lote__referencia').distinct()

        cursor_def = connection.cursor()
        grades2 = []
        for referencia in referencias:
            # Grade de solicitação
            context_ref = models.grade_solicitacao(
                cursor_def, referencia['lote__referencia'],
                solicit_id=solicit_id)
            context_ref.update({
                'style': {i: 'text-align: right;'
                          for i in range(2, len(context_ref['fields'])+1)},
            })
            grades2.append(context_ref)

        context.update({
            'grades2': grades2,
        })

        grade_total = models.grade_solicitacao(
            cursor_def, solicit_id=solicit_id)
        grade_total.update({
            'style': {i: 'text-align: right;'
                      for i in range(2, len(grade_total['fields'])+1)},
        })
        context.update({
            'gt': grade_total,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        if 'acao' in kwargs:
            acao = kwargs['acao']
        else:
            acao = None
        if 'id' in kwargs:
            slq_id = kwargs['id']
        else:
            slq_id = None
        solicit_id = kwargs['solicit_id']

        if acao == 'd' and slq_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.get(
                    id=slq_id)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        if acao == 'l' and solicit_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.filter(
                    solicitacao__id=solicit_id)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        # desreserva endereçados
        if acao == 'de' and solicit_id is not None:
            try:
                solicit_qtds = lotes.models.SolicitaLoteQtd.objects.filter(
                    solicitacao__id=solicit_id, lote__local__isnull=False)
                solicit_qtds.delete()
            except lotes.models.SolicitaLoteQtd.DoesNotExist:
                pass

        user = request_user(request)
        data = self.mount_context(solicit_id, user)
        context.update(data)
        return render(request, self.template_name, context)


class EnderecoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.AskLoteForm
        self.template_name = 'cd/endereco_lote.html'
        self.title_name = 'Verifica endereço de Lote'

    def mount_context(self, request, form):
        lote = form.cleaned_data['lote']

        context = {'lote': lote}

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        if lote_rec.local is None or lote_rec.local == '':
            local = 'Não endereçado'
            lotes_no_local = -1
        else:
            local = lote_rec.local
            lotes_no_local = len(lotes.models.Lote.objects.filter(
                local=lote_rec.local))

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': local,
            'q_lotes': lotes_no_local,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Grade(View):

    def __init__(self):
        self.Form_class = cd.forms.AskReferenciaForm
        self.template_name = 'cd/grade_estoque.html'
        self.title_name = 'Seleção de grade de estoque'

    def tipo(self, ref):
        if ref[0].isdigit():
            value = ('PA', 1, 'PA/PG')
        elif ref[0] in ('A', 'B'):
            value = ('PG', 2, 'PA/PG')
        elif ref[0] in ('F', 'Z'):
            value = ('MP', 4, 'MP')
        else:
            value = ('MD', 3, 'MD')
        return dict(zip(('tipo', 'ordem', 'grade'), value))

    def mount_context(self, request, ref, exec, limpo, page=1, detalhe=False):
        modelos_pagina = 5
        sel_modelos = []

        if ref == '':
            exec = 'busca'
        else:
            if ref[0] == '_':
                sel_modelos = ref[1:].split('_')
                ref = 'totais'
        todas = ref == 'todas'
        if todas:
            ref = ''
            exec = 'grade'
        totais = ref == 'totais'
        if totais:
            ref = ''
            exec = 'totais'

        refnum = int('0{}'.format(
            ''.join([c for c in ref if c.isdigit()])))
        context = {
            'ref': ref,
            'refnum': refnum,
            'detalhe': detalhe,
            'exec': exec,
        }
        if limpo:
            context['limpo'] = True

        cursor_def = connection.cursor()

        if totais:
            self.template_name = 'cd/grade_estoque_totais.html'

        if len(ref) == 5:  # Referência
            context.update({
                'link_tot': 1,
                'link_num': 1,
                'title_tipo': 1,
                'link_ref': 1,
            })
            referencias = [{
                'referencia': ref,
                'modelo': refnum,
            }]
            row = referencias[0]
            tipo = self.tipo(ref)
            row['tipo'] = tipo['tipo']
            row['ordem_tipo'] = tipo['ordem']
            row['grade_tipo'] = tipo['grade']

            modelos = [refnum]
            exec = 'grade'
        else:  # Todos ou Modelo ou Totais
            data_rec = lotes.models.Lote.objects
            data_rec = data_rec.exclude(
                local__isnull=True
            ).exclude(
                local__exact=''
            ).exclude(
                qtd__lte=0)

            referencias = data_rec.distinct().values(
                'referencia').order_by('referencia')
            for row in referencias:
                row['modelo'] = int(
                    ''.join([c for c in row['referencia'] if c.isdigit()]))

            if len(sel_modelos) > 0:
                refs_copy = referencias[:]
                referencias = [row for row in refs_copy
                               if str(row['modelo']) in sel_modelos]

            if refnum == 0:  # Todos ou Totais ou busca vazio
                for row in referencias:
                    row['referencia|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['referencia']])
                    row['modelo|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['modelo']])
                    tipo = self.tipo(row['referencia'])
                    row['tipo'] = tipo['tipo']
                    row['ordem_tipo'] = tipo['ordem']
                    row['grade_tipo'] = tipo['grade']
                referencias = sorted(
                    referencias, key=lambda k: (
                        k['modelo'], k['ordem_tipo'], k['referencia']))
                if exec == 'busca':
                    context.update({
                        'link_tot': 1,
                    })
                    group = ['modelo']
                    group_rowspan(referencias, group)
                    context.update({
                        'headers': ['Grades por referência numérica', 'Tipo',
                                    'Grade de referência'],
                        'fields': ['modelo', 'tipo', 'referencia'],
                        'group': group,
                        'data': referencias,
                    })
                else:  # exec == 'grade'
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        'link_num_hr': 1,
                        'title_tipo': 1,
                        'title_tipo_hr': 1,
                        'link_ref': 1,
                    })
                    modelos = []
                    for ref in referencias:
                        if ref['modelo'] not in modelos:
                            modelos.append(ref['modelo'])
            else:  # Modelo ou busca
                referencias = [
                    {'referencia': row['referencia'],
                     'modelo': refnum,
                     }
                    for row in referencias
                    if row['modelo'] == refnum]
                for row in referencias:
                    row['referencia|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['referencia']])
                    tipo = self.tipo(row['referencia'])
                    row['tipo'] = tipo['tipo']
                    row['ordem_tipo'] = tipo['ordem']
                    row['grade_tipo'] = tipo['grade']
                referencias = sorted(
                    referencias, key=lambda k: (
                        k['ordem_tipo'], k['referencia']))

                if exec == 'busca':
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        })
                    context.update({
                        'headers': ['Tipo', 'Grade de referência'],
                        'fields': ['tipo', 'referencia'],
                        'data': referencias,
                    })
                else:  # exec == 'grade'
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        'title_tipo': 1,
                        'title_tipo_hr': 1,
                        'link_ref': 1,
                    })
                    modelos = [refnum]

        if exec in ['grade', 'totais']:
            if not totais:
                paginator = Paginator(modelos, modelos_pagina)
                try:
                    modelos = paginator.page(page)
                except PageNotAnInteger:
                    modelos = paginator.page(1)
                except EmptyPage:
                    modelos = paginator.page(paginator.num_pages)
            grades_ref = []
            for modelo in modelos:
                refnum_ant = -1
                tipo_ant = '##'
                mod_referencias = [
                    ref for ref in referencias if ref['modelo'] == modelo]
                if totais:
                    mod_referencias_todos = []
                else:  # todos ou modelo
                    mod_referencias_todos = mod_referencias
                for row in mod_referencias_todos:
                    ref = row['referencia']

                    invent_ref = models.grade_solicitacao(
                        cursor_def, ref, tipo='i', grade_inventario=True)
                    grade_ref = {
                        'ref': ref,
                        'inventario': invent_ref,
                        }
                    if refnum_ant != row['modelo']:
                        grade_ref.update({'refnum': row['modelo']})
                        refnum_ant = row['modelo']
                        tipo_ant = '##'

                    if tipo_ant != row['grade_tipo']:
                        grade_ref.update({'tipo': row['grade_tipo']})
                        tipo_ant = row['grade_tipo']

                    solped_ref = models.grade_solicitacao(
                        cursor_def, ref, tipo='sp', grade_inventario=True)
                    if solped_ref['total'] != 0:
                        dispon_ref = models.grade_solicitacao(
                            cursor_def, ref, tipo='i-sp',
                            grade_inventario=True)
                        grade_ref.update({
                            'solped': solped_ref,
                            'disponivel': dispon_ref,
                            })
                        if detalhe:
                            solic_ref = models.grade_solicitacao(
                                cursor_def, ref, tipo='s',
                                grade_inventario=True)
                            if solic_ref['total'] != 0:
                                grade_ref.update({
                                    'solicitacoes': solic_ref,
                                    })
                            pedido_ref = models.grade_solicitacao(
                                cursor_def, ref, tipo='p',
                                grade_inventario=True)
                            if pedido_ref['total'] != 0:
                                grade_ref.update({
                                    'pedido': pedido_ref,
                                    })

                    grades_ref.append(grade_ref)

                refs = []
                if totais:
                    totaliza_mais_que = 0
                else:
                    totaliza_mais_que = 1
                if len(mod_referencias) > totaliza_mais_que:
                    refs = [row['referencia'] for row in mod_referencias
                            if row['grade_tipo'] == 'PA/PG']

                if len(refs) > totaliza_mais_que:
                    dispon_modelo = models.grade_solicitacao(
                        cursor_def, refs, tipo='i-sp')
                    if dispon_modelo['total'] != 0:

                        if totais:  # se for totais add borda entre as colunas
                            for i in range(1, len(dispon_modelo['fields'])):
                                i_column = i + 1
                                ori_style = ''
                                if i_column in dispon_modelo['style']:
                                    ori_style = dispon_modelo[
                                        'style'][i_column]
                                dispon_modelo['style'][i_column] = \
                                    ori_style + \
                                    'border-left-style: solid;' \
                                    'border-left-width: thin;'

                        grade_ref = {
                            'ref': '',
                            'refnum': row['modelo'],
                            'tipo': 'PA/PG',
                            'titulo': 'Total disponível',
                            'inventario': dispon_modelo,
                        }
                        if totais:
                            grade_ref.update({'titulo': '-'})
                            grade_ref.update({'refnum': modelo})
                        grades_ref.append(grade_ref)

            if totais:
                refs = [row['referencia'] for row in referencias
                        if row['grade_tipo'] == 'PA/PG']
                dispon_sel_modelo = models.grade_solicitacao(
                    cursor_def, refs, tipo='i-sp')

                for i in range(1, len(dispon_sel_modelo['fields'])):
                    i_column = i + 1
                    ori_style = ''
                    if i_column in dispon_sel_modelo['style']:
                        ori_style = dispon_sel_modelo[
                            'style'][i_column]
                    dispon_sel_modelo['style'][i_column] = \
                        ori_style + \
                        'border-left-style: solid;' \
                        'border-left-width: thin;'
                grade_ref = {
                    'ref': '',
                    'tipo': 'PA/PG',
                    'titulo': '-',
                    'inventario': dispon_sel_modelo,
                }
                grade_ref.update({'refnum': 'TOTAL'})
                grades_ref.append(grade_ref)

            context.update({
                'grades': grades_ref,
                'modelos': modelos,
                'modelos_pagina': modelos_pagina,
                })

        return context

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        limpo = request.GET.get('limpo', 'N') == 'S'
        if 'referencia' in kwargs and kwargs['referencia'] is not None:
            ref = kwargs['referencia']
        else:
            ref = ''
        if 'detalhe' in kwargs and kwargs['detalhe'] is not None:
            detalhe = kwargs['detalhe'] == 'detalhe'
        else:
            detalhe = False
        context = {'titulo': self.title_name}
        data = self.mount_context(request, ref, 'grade', limpo, page, detalhe)
        context.update(data)
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            ref = form.cleaned_data['ref']
            data = self.mount_context(request, ref, 'busca', False)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Historico(View):

    def __init__(self):
        self.Form_class = cd.forms.HistoricoForm
        self.template_name = 'cd/historico.html'
        self.title_name = 'Histórico de OP'

    def mount_context(self, cursor, op):
        context = {
            'op': op,
            }

        data = models.historico(cursor, op)
        if len(data) == 0:
            context.update({'erro': 'Sem lotes ativos'})
            return context
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
        context.update({
            'headers': ('Data', 'Qtd. de lotes', 'Endereço', 'Usuário'),
            'fields': ('dt', 'qtd', 'endereco', 'usuario'),
            'data': data,
        })

        data = models.historico_detalhe(cursor, op)
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
            row['lote|TARGET'] = '_BLANK'
            row['lote|LINK'] = reverse(
                'cd:historico_lote', args=[row['lote']])
        context.update({
            'd_headers': ('Lote', 'Última data', 'Endereço', 'Usuário'),
            'd_fields': ('lote', 'dt', 'endereco', 'usuario'),
            'd_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class HistoricoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.ALoteForm
        self.template_name = 'cd/historico_lote.html'
        self.title_name = 'Histórico de lote'

    def mount_context(self, cursor, lote):
        context = {
            'lote': lote,
            }

        data = models.historico_lote(cursor, lote)
        if len(data) == 0:
            context.update({'erro': 'Lote não encontrado ou nunca endereçado'})
            return context
        old_estagio = None
        old_usuario = None
        old_local = None
        for row in data:
            n_info = 0
            log = row['log']
            log = log.replace("<UTC>", "utc")
            log = re.sub(
                r'^(.*)<SimpleLazyObject: <User: ([^\s]*)>>(.*)$',
                r'\1"\2"\3', log)
            dict_log = eval(log)

            if 'estagio' in dict_log:
                row['estagio'] = dict_log['estagio']
                old_estagio = row['estagio']
                n_info += 1
            else:
                if old_estagio is None:
                    row['estagio'] = '-'
                else:
                    row['estagio'] = '='
            if row['estagio'] == 999:
                row['estagio'] = 'Finalizado'

            if 'local' in dict_log:
                row['local'] = dict_log['local']
                old_local = row['local']
                n_info += 1
            else:
                if old_local is None:
                    row['local'] = '-'
                else:
                    row['local'] = '='
            if row['local'] is None:
                row['local'] = 'SAIU!'

            if 'local_usuario' in dict_log:
                row['local_usuario'] = dict_log['local_usuario']
                old_usuario = row['local_usuario']
                n_info += 1
            else:
                if old_usuario is None or row['local'] in ('-', '='):
                    row['local_usuario'] = '-'
                else:
                    row['local_usuario'] = '='

            row['n_info'] = n_info

        context.update({
            'headers': ('Data', 'Estágio', 'Local', 'Usuário'),
            'fields': ('time', 'estagio', 'local', 'local_usuario'),
            'data': [row for row in data if row['n_info'] != 0],
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, lote))
        context['form'] = form
        return render(request, self.template_name, context)
