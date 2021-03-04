from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

import produto.forms as forms
import produto.queries as queries


class BuscaModelo(View):
    Form_class = forms.FiltroModeloForm
    template_name = 'produto/busca_modelos.html'
    title_name = 'Listagem de modelos'

    def mount_context(self, cursor, descricao):
        context = {'descricao': descricao}

        data = queries.busca_modelo(cursor, descricao)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum modelo selecionado',
            })
            return context

        for row in data:
            if row['modelo'] is None:
                row['modelo'] = '-'

        headers = ['Modelo', 'Descrição']
        fields = ['modelo', 'descr']
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
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
            descricao = form.cleaned_data['descricao']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, descricao))
        context['form'] = form
        return render(request, self.template_name, context)
