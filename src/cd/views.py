from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

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

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco).order_by(
                '-local_at'
                ).values(
                    'op', 'lote', 'qtd_produzir',
                    'referencia', 'cor', 'tamanho',
                    'local_at', 'local_usuario__username')
        if len(lotes_no_local):
            # pprint(lotes_no_local)
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
        ordem = form.cleaned_data['ordem']

        context = {'endereco': endereco,
                   'lote': lote,
                   'op': op,
                   'ref': ref,
                   'tam': tam,
                   'cor': cor,
                   'ordem': ordem,
                   }

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
        else:  # Endereço OP Referência Cor Tamanho Lote
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
        # pprint(data)
        # pprint(data[0])
        # pprint(list(data_rec.values()[:3]))
        # print('len ->>>>>>>>>', len(data_rec.values()[:3]))
        # for row in data_rec[:3]:
        #     pprint(row.lote)
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
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
            data = self.mount_context(cursor, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
