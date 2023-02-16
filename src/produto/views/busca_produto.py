from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import produto.forms as forms
import produto.queries as queries


class Busca(View):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.FiltroRefForm
        self.template_name = 'produto/busca.html'
        self.title_name = 'Listagem de produtos'

    def mount_context(self, cursor, filtro, cor, roteiro, alternativa, colecao):
        context = {'filtro': filtro}

        colecao_codigo = colecao.colecao if colecao else None
        data = queries.busca_produto(
            cursor,
            filtro=filtro,
            cor=cor,
            roteiro=roteiro,
            alternativa=alternativa,
            colecao=colecao_codigo,
        )
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum produto selecionado',
            })
        else:
            for row in data:
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
                if row['ALTERNATIVA'] is None:
                    row['ALTERNATIVA'] = '-'
                if row['ROTEIRO'] is None:
                    row['ROTEIRO'] = '-'
                if row['CNPJ9'] is None:
                    row['CNPJ9'] = 0
                if row['CNPJ4'] is None:
                    row['CNPJ4'] = 0
                if row['CNPJ2'] is None:
                    row['CNPJ2'] = 0
                if row['CNPJ9'] == 0:
                    row['CLIENTE'] = '-'
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['CLIENTE'])

            headers = ['#', 'Tipo', 'Referência', 'Descrição',
                       'Status (Responsável)', 'Cliente', 'Coleção']
            fields = ['NUM', 'TIPO', 'REF', 'DESCR',
                      'RESP', 'CLIENTE', 'COLECAO']
            if len(cor) != 0:
                headers.append('Cor')
                headers.append('Cor Descr.')
                fields.append('COR')
                fields.append('COR_DESC')

            if roteiro is not None or alternativa is not None:
                headers.append('Alternativa')
                fields.append('ALTERNATIVA')
                headers.append('Roteiro')
                fields.append('ROTEIRO')

            context.update({
                'headers': headers,
                'fields': fields,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'filtro' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'filtro' in kwargs:
            form.data['filtro'] = kwargs['filtro']
        if form.is_valid():
            filtro = form.cleaned_data['filtro']
            cor = form.cleaned_data['cor']
            roteiro = form.cleaned_data['roteiro']
            alternativa = form.cleaned_data['alternativa']
            colecao = form.cleaned_data['colecao']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, filtro, cor, roteiro, alternativa, colecao))
        context['form'] = form
        return render(request, self.template_name, context)
