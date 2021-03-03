from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission

from estoque import forms, queries


class ConfrontaEstoque(View):
    Form_class = forms.ConfrontaEstoqueForm
    template_name = 'estoque/confronta_estoque.html'
    title_name = 'Confronta estoque e transações'

    def mount_context(self, request, cursor, ref, tam, cor, deposito, botao):
        context = {
            'permission': has_permission(
                request, 'base.can_adjust_stock'),
        }

        if len(ref) == 0 and botao == 'v':
            context.update({'erro': 'Digite algo em Referência ou modelo'})
            return context

        context.update({
            'nivel': 1,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'botao': botao,
        })

        modelo = None
        if len(ref) == 5:
            context.update({
                'ref': ref,
            })
        else:
            modelo = ref.lstrip("0")
            ref = ''
            context.update({
                'modelo': modelo,
            })
        data, exec_ok, count = queries.confronta_estoque_transacoes(
            cursor,
            deposito=deposito,
            modelo=modelo,
            ref=ref,
            tam=tam,
            cor=cor,
            corrige=(botao == 'c'),
            )
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'exec_ok': exec_ok,
            'count': count,
        })

        if len(ref) == 0 and botao == 'c':
            return context

        for row in data:
            if row['stq'] == (row['qtd_old'] + row['qtd']):
                row['status'] = 'OK'
            else:
                row['status'] = 'Errado'
        context.update({
            'headers': ('Depósito', 'Referência', 'Cor',
                        'Tamanho', 'Trasações fechadas',
                        'Trasações abertas', 'Estoque', 'Status'),
            'fields': ('dep', 'ref', 'cor',
                       'tam', 'qtd_old',
                       'qtd', 'stq', 'status'),
            'data': data,
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                },
        })

        return context

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        context = {'titulo': self.title_name}
        form = self.Form_class(cursor=cursor)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST, cursor=cursor)
        if form.is_valid():
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            botao = 'c' if 'corrige' in request.POST else 'v'
            context.update(self.mount_context(
                request, cursor, ref, tam, cor, deposito, botao))
        context['form'] = form
        return render(request, self.template_name, context)
