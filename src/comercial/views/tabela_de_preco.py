from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

import comercial.forms as forms


class TabelaDePreco(View):
    Form_class = forms.TabalaDePrecoForm
    template_name = 'comercial/tabela_de_preco.html'
    title_name = 'Tabela de preços'

    def mount_context(self, cursor, tabela):
        context = {'tabela': tabela}

        # data = queries.por_cliente(cursor, cliente=cliente)
        data = []
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            row['REF|LINK'] = reverse(
                'produto:info_xml__get', args=[row['REF']])

        headers = [
            'Referência', 'Descrição', 'Cliente']
        fields = [
            'REF', 'DESCR', 'CLIENTE']

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'tabela' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'tabela' in kwargs:
            form.data['tabela'] = kwargs['tabela']
        if form.is_valid():
            tabela = form.cleaned_data['tabela']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, tabela))
        context['form'] = form
        return render(request, self.template_name, context)
