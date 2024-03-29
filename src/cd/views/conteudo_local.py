import re
from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View
from cd.classes.palete import Plt

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.functions.strings import only_digits

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    conteudo_local,
    get_endereco,
    get_esvaziamentos_de_palete,
    get_palete,
)


class ConteudoLocal(View):

    _PALETE = 0
    _ENDERECO = 1
    _ERRO = 2
    _INTEGER = 3
    _NOME_TIPO_LOCAL = ['palete', 'endereço', 'código']


    def __init__(self):
        self.Form_class = cd.forms.ConteudoLocalForm
        self.template_name = 'cd/conteudo_local.html'
        self.context = {'titulo': 'Conteúdo'}

    def dt_to_dtget(self, data_versao):
        return data_versao.strftime('%Y%m%d%H%M%S')

    def get_esvaziamentos(self):
        dados_esvaziamento = get_esvaziamentos_de_palete(self.cursor, self.local)

        if dados_esvaziamento:

            for row in dados_esvaziamento:
                row['dh|LINK'] = reverse(
                    'cd:vizualiza_esvaziamento',
                    args=[self.local, self.dt_to_dtget(row['dh'])]
                )

            self.context.update({
                'e_headers': ['Data/hora'],
                'e_fields': ['dh'],
                'e_data': dados_esvaziamento,
            })

    def get_lotes(self):
        headers = ["Bipado", "Lote", "OP", 'Item', 'Qtd.']
        fields = ['data', 'lote', 'op', 'item', 'qtd']

        if self.tipo_local == self._PALETE:
            enderecos = set()
            for row in self.lotes_end:
                if row['endereco']:
                    enderecos.add(row['endereco'])
            self.context.update({
                'endereco_lotes': ', '.join(enderecos),
            })
            endereco_links = []
            for endereco in enderecos:
                endereco_url = reverse(
                    'cd:conteudo_local',
                    args=[endereco]
                )
                endereco_link = f'<a href="{endereco_url}">{endereco}</a>'
                endereco_links.append(endereco_link)
            self.context.update({
                'endereco_link': ', '.join(endereco_links),
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
            palete_links = []
            for palete in paletes:
                palete_url = reverse(
                    'cd:conteudo_local',
                    args=[palete]
                )
                palete_link = f'<a href="{palete_url}">{palete}</a>'
                palete_links.append(palete_link)
            self.context.update({
                'palete_link': ', '.join(palete_links),
            })
            if len(paletes) > 1:
                headers += ['Palete']
                fields += ['palete']

        total_qtd = 0
        dados = []
        ult_data = datetime(3000, 1, 1)
        for row in self.lotes_end:
            if row['data'].date() < ult_data.date():
                ult_data = row['data']
                dados.append({
                    'data': ult_data.strftime("%d/%m/%y"),
                    'data|STYLE': "font-weight: bold;",
                    'lote': '',
                    'op': '',
                    'item': '',
                    'qtd': '',
                    'palete': '',
                    'endereco': '',
                    'retira': '',
                })
            dados.append(row)
            total_qtd += row['qtd']
            row['op'] = f"{row['op']}"
            row['data'] = row['data'].strftime("%H:%M:%S")
            row['lote|LINK'] = reverse(
                'cd:localiza_lote',
                args=[row['lote']]
            )
            if not row['endereco']:
                row['endereco'] = '-'
            row['retira'] = 'X'
            row['retira|LINK'] = reverse(
                'cd:retira_lote',
                args=[row['lote']]
            )
            row['retira|TARGET'] = '_blank'

        if has_permission(self.request, 'cd.can_del_lote_de_palete'):
            headers.append('Retira')
            fields.append('retira')

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': dados,
            'style': {
                5: 'text-align: right;',
            },
            'qtd_lotes': len(self.lotes_end),
            'total_qtd': total_qtd,
        })

    def local_ok(self):
        if self.tipo_local == self._PALETE:
            return get_palete(self.cursor, self.local)
        elif self.tipo_local == self._ENDERECO:
            return get_endereco(self.cursor, self.local)
        elif self.tipo_local == self._INTEGER:
            local = only_digits(self.local)
            if local:
                local = int(local)
                palete = Plt().mount(local)
                if get_palete(self.cursor, palete):
                    self.local = palete
                    self.tipo_local = self._PALETE
                    return True
            self.tipo_local = self._ERRO
        return False

    def get_tipo_local(self, local):
        if re.match("^P[L0-9][T0-9][0-9]{4}[A-Z]$", local):
            return self._PALETE
        elif re.match("^CALHA[0-9]{2}[A-Z]$", local):
            return self._PALETE
        elif re.match("^[12][A-Z]{1,2}[0-9]{4}$", local):
            return self._ENDERECO
        elif re.match("^[0-9]+$", local):
            return self._INTEGER
        else:
            return self._ERRO

    def mount_context(self, request, form):
        self.cursor = db_cursor_so(request)

        self.local = form.cleaned_data['local'].upper()

        self.tipo_local = self.get_tipo_local(self.local)
        nome_tipo_local = self._NOME_TIPO_LOCAL[self.tipo_local]
        if not self.local_ok():
            self.context.update({
                'erro': f"{nome_tipo_local.capitalize()} inexistênte."})
            return

        self.context.update({
            'local': self.local,
            'nome_tipo_local': nome_tipo_local,
        })

        self.lotes_end = conteudo_local(
            self.cursor,
            local=self.local,
            item_qtd63=True,
        )

        tem_lotes = self.lotes_end and self.lotes_end[0]['lote']

        if tem_lotes:
            self.get_lotes()
        else:
            self.context.update({
                'erro': f"Zero lote no {nome_tipo_local} {self.local}."})

        if self.tipo_local == self._PALETE:
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
