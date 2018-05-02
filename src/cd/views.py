from pprint import pprint
from datetime import timedelta

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from fo2.models import rows_to_dict_list_lower

import lotes.models

import cd.forms


def index(request):
    context = {}
    return render(request, 'cd/index.html', context)


class LotelLocal(PermissionRequiredMixin, View):
    permission_required = 'lotes.can_inventorize_lote'
    Form_class = cd.forms.LoteForm
    template_name = 'cd/lote_local.html'
    title_name = 'Inventariar 63'

    def mount_context(self, request, cursor, form):
        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        identificado = form.cleaned_data['identificado']

        if endereco == 'SAI':
            endereco = None

        context = {'endereco': endereco}

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context
        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': lote_rec.local,
            })

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
            cursor = connections['so'].cursor()
            data = self.mount_context(request, cursor, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class TrocaLocal(PermissionRequiredMixin, View):
    permission_required = 'lotes.can_relocate_lote'
    Form_class = cd.forms.TrocaLocalForm
    template_name = 'cd/troca_local.html'
    title_name = 'Trocal endereço'

    def mount_context(self, request, cursor, form):
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
            cursor = connections['so'].cursor()
            data = self.mount_context(request, cursor, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Estoque(View):
    Form_class = cd.forms.EstoqueForm
    template_name = 'cd/estoque.html'
    title_name = 'Estoque 63'

    def mount_context(self, cursor, form):
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
            headers = ('Em', 'Por', 'Endereço', 'Lote',
                       'Referência', 'Tamanho', 'Cor', 'Quant', 'OP')
            fields = ('local_at', 'local_usuario__username', 'local', 'lote',
                      'referencia', 'tamanho', 'cor', 'qtd_produzir', 'op')
        elif ordem == 'O':  # OP Referência Cor Tamanho Endereço Lote
            data_rec = data_rec.order_by(
                'op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote')
            headers = ('OP', 'Referência', 'Tamanho', 'Cor', 'Quant',
                       'Endereço', 'Lote', 'Em', 'Por')
            fields = ('op', 'referencia', 'tamanho', 'cor', 'qtd_produzir',
                      'local', 'lote', 'local_at', 'local_usuario__username')
        elif ordem == 'R':  # Referência Cor Tamanho Endereço OP Lote
            data_rec = data_rec.order_by(
                'referencia', 'cor', 'ordem_tamanho', 'local', 'op', 'lote')
            headers = ('Referência', 'Tamanho', 'Cor', 'Quant',
                       'Endereço', 'OP', 'Lote', 'Em',
                       'Por')
            fields = ('referencia', 'tamanho', 'cor', 'qtd_produzir',
                      'local', 'op', 'lote', 'local_at',
                      'local_usuario__username')
        else:  # E: Endereço OP Referência Cor Tamanho Lote
            data_rec = data_rec.order_by(
                'local', 'op', 'referencia', 'cor', 'ordem_tamanho', 'lote')
            headers = ('Endereço', 'OP', 'Referência', 'Tamanho', 'Cor',
                       'Quant', 'Lote',
                       'Em', 'Por')
            fields = ('local', 'op', 'referencia', 'tamanho', 'cor',
                      'qtd_produzir', 'lote',
                      'local_at', 'local_usuario__username')

        data = data_rec.values(
            'local', 'local_at', 'local_usuario__username', 'op', 'lote',
            'referencia', 'tamanho', 'cor', 'qtd_produzir')
        for row in data:
            row['op|LINK'] = reverse(
                'op_op', args=[row['op']])
            row['lote|LINK'] = reverse(
                'posicao_lote', args=[row['lote']])
            row['local|LINK'] = reverse(
                'cd_estoque_filtro', args=['E', row['local']])
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
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
            cursor = connections['so'].cursor()
            data = self.mount_context(cursor, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Inconsistencias(View):
    # Form_class = cd.forms.EstoqueForm
    template_name = 'cd/inconsist.html'
    title_name = 'Inconsistências Systêxtil 63'

    def mount_context(self, cursor, ordem, opini):
        step = 10
        data_size = 30
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
                        op__gte=opini
                    )
            else:
                if opini == 0:
                    ops = ops.filter(
                            op__lte=999999999
                        )
                else:
                    ops = ops.filter(
                            op__lte=opini
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
                WHERE op.COD_CANCELAMENTO = 0
                  AND ({filtro})
                GROUP BY
                  op.ORDEM_PRODUCAO
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
                    'cd_estoque_filtro', args=['O', op['op']])
                row['op|TARGET'] = '_blank'
                row['cr'] = ''
                estagios_op = [r for r in estagios if r['op'] == op['op']]
                if len(estagios_op) == 0:
                    row['cr'] = 'OP sem estágio 63'
                else:
                    for estagio_op in estagios_op:
                        if estagio_op['est'] is None:
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
            if ordem == 'A':
                context.update({'opnext': data[data_size-1]['op']+1})
            else:
                context.update({'opnext': data[data_size-1]['op']-1})
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
            opini = 0

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
