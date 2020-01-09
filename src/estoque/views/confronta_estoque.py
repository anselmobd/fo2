from django.db import connections
from django.shortcuts import render
from django.views import View

from estoque import forms
from estoque import queries


class ConfrontaEstoque(View):
    Form_class = forms.RecalculaEstoqueForm
    template_name = 'estoque/confronta_estoque.html'
    title_name = 'Confronta estoque e transações'

    def mount_context(self, cursor, ref, tam, cor, deposito):
        context = {
            'nivel': 1,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            }
        modelo = None
        if len(ref) % 5 == 0:
            context.update({
                'ref': ref,
            })
        else:
            modelo = ref.lstrip("0")
            ref = ''
            context.update({
                'modelo': modelo,
            })
        data = queries.confronta_estoque_transacoes(
            cursor,
            deposito=deposito,
            modelo=modelo,
            ref=ref,
            tam=tam,
            cor=cor,
            )
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        context.update({
            'headers': ('Depósito', 'Referência', 'Cor',
                        'Tamanho', 'Quantidades fechada',
                        'Quantidades aberta', 'Estoque'),
            'fields': ('dep', 'ref', 'cor',
                       'tam', 'qtd_old',
                       'qtd', 'stq'),
            'data': data,
            'style': {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                },
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
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, ref, tam, cor, deposito))
        context['form'] = form
        return render(request, self.template_name, context)
