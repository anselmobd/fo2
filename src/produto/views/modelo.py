from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import produto.forms as forms
import produto.queries as queries


class Modelo(View):
    Form_class = forms.ModeloForm
    template_name = 'produto/modelo.html'
    title_name = 'Modelo (número do PA)'

    def mount_context(self, cursor, modelo):
        context = {'modelo': modelo}

        if len(modelo) not in range(1, 6):
            context.update({
                'msg_erro': 'Modelo inválido',
            })
            return context

        # Informações básicas
        data = queries.modelo_inform(cursor, modelo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Modelo não encontrado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
                if row['CNPJ9'] == 0:
                    row['CLIENTE'] = ''
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers': ('Tipo', 'Referência', 'Descrição',
                            'Coleção', 'Coleção cliente',
                            'Cliente', 'Status (Responsável)'),
                'fields': ('TIPO', 'REF', 'DESCR',
                           'COLECAO', 'COLECAO_CLIENTE',
                           'CLIENTE', 'STATUS'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'modelo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'modelo' in kwargs:
            form.data['modelo'] = kwargs['modelo']
        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, modelo))
        context['form'] = form
        return render(request, self.template_name, context)

