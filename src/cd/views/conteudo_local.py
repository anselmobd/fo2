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
    get_palete,
)


class ConteudoLocal(View):

    def __init__(self):
        self.Form_class = cd.forms.ConteudoLocalForm
        self.template_name = 'cd/conteudo_local.html'
        self.context = {'titulo': 'Conteúdo'}

    def get_esvaziamentos(self):
        if not self.eh_palete:
            return

        dados_esvaziamento = get_esvaziamentos_de_palete(self.cursor, self.local)

        if dados_esvaziamento:
            self.context.update({
                'e_headers': ['Data/hora'],
                'e_fields': ['dh'],
                'e_data': dados_esvaziamento,
            })

    def get_lotes(self):
        headers = ["Bipado em", "Lote", "OP"]
        fields = ['data', 'lote', 'op']

        if self.eh_palete:
            enderecos = set()
            for row in self.lotes_end:
                if row['endereco']:
                    enderecos.add(row['endereco'])
            self.context.update({
                'endereco_lotes': ', '.join(enderecos),
            })
            if len(enderecos) > 1:
                headers += ['Endereço']
                fields += ['endereco']
        else:
            paletes = set()
            for row in self.lotes_end:
                if row['palete']:
                    paletes.add(row['palete'])
            self.context.update({
                'palete_lotes': ', '.join(paletes),
            })
            if len(paletes) > 1:
                headers += ['Palete']
                fields += ['palete']

        dados = []
        ult_data = datetime(3000, 1, 1)
        for row in self.lotes_end:
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

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': dados,
        })

    def palete_ok(self, palete):
        dados_palete = get_palete(self.cursor, palete)
        if not dados_palete:
            self.context.update({
                'erro': "Palete inexistênte."})
            return False
        return True

    def local_ok(self):
        if self.eh_palete:
            return self.palete_ok(self.local)
        return True

    def mount_context(self, request, form):
        self.cursor = db_cursor_so(request)

        self.local = form.cleaned_data['local'].upper()
        self.eh_palete = len(self.local) == 8
        self.context.update({
            'local': self.local,
            'eh_palete': self.eh_palete,
        })

        if not self.local_ok():
            return

        self.lotes_end = lotes_em_endereco(self.cursor, self.local)

        if (not self.lotes_end) or (not self.lotes_end[0]['lote']):
            self.context.update({
                'erro': 'Nenhum lote no endereço.'})
            self.get_esvaziamentos()
            return

        self.get_lotes()

        self.get_esvaziamentos()

    def get(self, request, *args, **kwargs):
        if 'local' in kwargs and kwargs['local']:
            return self.post(request, *args, **kwargs)
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if 'local' in kwargs and kwargs['local']:
            form = self.Form_class(kwargs)
        else:
            form = self.Form_class(request.POST)
        if form.is_valid():
            self.mount_context(request, form)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
