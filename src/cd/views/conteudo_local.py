from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    lotes_em_endereco,
    get_esvaziamentos_de_palete,
)


class ConteudoLocal(View):

    def __init__(self):
        self.Form_class = cd.forms.ConteudoLocalForm
        self.template_name = 'cd/conteudo_local.html'
        self.title_name = 'Conteúdo'

    def add_esvaziamento(self, cursor, codigo, context):
        dh_esvaziamento = get_esvaziamentos_de_palete(cursor, codigo)

        if dh_esvaziamento:
            context.update({
                'e_headers': ['Data/hora'],
                'e_fields': ['dh'],
                'e_data': dh_esvaziamento,
            })

    def mount_context(self, request, form):
        cursor = db_cursor_so(request)

        codigo = form.cleaned_data['codigo'].upper()
        context = {'endereco': codigo}

        lotes_end = lotes_em_endereco(cursor, codigo)

        eh_palete = len(codigo) == 8

        if (not lotes_end) or (not lotes_end[0]['lote']):
            context.update({
                'erro': 'Nenhum lote no endereço.'})
            if eh_palete:
                self.add_esvaziamento(cursor, codigo, context)
            return context

        headers = ["Bipado em", "Lote", "OP"]
        fields = ['data', 'lote', 'op']

        if eh_palete:
            enderecos = set()
            for row in lotes_end:
                if row['endereco']:
                    enderecos.add(row['endereco'])
            context.update({
                'endereco_lotes': ', '.join(enderecos),
            })
            if len(enderecos) > 1:
                headers += ['Endereço']
                fields += ['endereco']
        else:
            paletes = set()
            for row in lotes_end:
                if row['palete']:
                    paletes.add(row['palete'])
            context.update({
                'palete_lotes': ', '.join(paletes),
            })
            if len(paletes) > 1:
                headers += ['Palete']
                fields += ['palete']

        dados = []
        ult_data = datetime(3000, 1, 1)
        for row in lotes_end:
            if row['data'].date() < ult_data.date():
                ult_data = row['data']
                dados.append({
                    'data': ult_data.strftime("%m/%d/%y"),
                    'data|STYLE': "font-weight: bold;",
                    'lote': '',
                    'op': '',
                    'palete': '',
                    'endereco': '',
                })
            dados.append(row)
            row['data'] = row['data'].strftime("%H:%M:%S")
            row['lote|LINK'] = reverse(
                'cd:localiza_lote',
                args=[row['lote']]
            )
            if not row['endereco']:
                row['endereco'] = '-'

        context.update({
            'eh_palete': eh_palete,
            'headers': headers,
            'fields': fields,
            'data': dados,
        })

        if eh_palete:
            self.add_esvaziamento(cursor, codigo, context)

        return context

    def get(self, request, *args, **kwargs):
        if 'codigo' in kwargs and kwargs['codigo']:
            return self.post(request, *args, **kwargs)
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        if 'codigo' in kwargs and kwargs['codigo']:
            form = self.Form_class(kwargs)
        else:
            form = self.Form_class(request.POST)
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
