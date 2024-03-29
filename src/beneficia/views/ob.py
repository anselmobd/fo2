from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import  db_cursor_so

from utils.functions.strings import is_only_digits
from utils.functions.views import Fo2ViewMethods
from utils.views import totalize_data

from beneficia.forms.main import ObForm
from beneficia.queries import (
    busca_ob,
    ob_destinos,
    ob_estagios,
    ob_tecidos,
)


__all__ = ['Ob']


class Ob(View, Fo2ViewMethods):

    def __init__(self):
        super().__init__()
        self.Form_class = ObForm
        self.template_name = 'beneficia/ob.html'
        self.title_name = 'OB'
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados = busca_ob.query(self.cursor, self.context['ob'])
        if len(dados) == 0:
            return

        for row in dados:
            row['data'] = row['data'].date()
            if is_only_digits(row['os']):
                row['os|TARGET'] = '_blank'
                row['os|LINK'] = reverse(
                    'producao:os__get', args=[row['os']])
            if is_only_digits(row['op']):
                row['op|TARGET'] = '_blank'
                row['op|LINK'] = reverse(
                    'producao:op__get', args=[row['op']])

        self.context.update({
            'headers': [
                'Período',
                'Data Programa',
                'Equipamento',
                'Rolos',
                'Quilos',
                'Situação',
                'Cancelamento',
                'Obs.',
                'OS',
                'OP',
            ],
            'fields': [
                'periodo',
                'data',
                'maq',
                'rolos',
                'quilos',
                'sit',
                'canc',
                'obs',
                'os',
                'op',
            ],
            'dados': dados,
        })

        est_dados = ob_estagios.query(self.cursor, self.context['ob'])
        self.context.update({
            'est_headers': (
                'Sequência',
                'Estágio',
                'Descrição',
                'Início',
                'Operador Início',
                'Término',
                'Operador Término',
            ),
            'est_fields': (
                'seq',
                'est',
                'est_descr',
                'ini',
                'usuario_ini',
                'fim',
                'usuario_fim',
            ),
            'est_dados': est_dados,
        })

        tec_dados = ob_tecidos.query(self.cursor, self.context['ob'])
        self.context.update({
            'tec_headers': [
                'Nível',
                'Ref.',
                'Tam.',
                'Cor',
                'Alt.',
                'Rot.',
                'Rolos prog.',
                'Quilos prog.',
                'Rolos real',
                'Quilos real',
                'Rolos prod.',
                'Quilos prod.',
            ],
            'tec_fields': [
                'nivel',
                'ref',
                'tam',
                'cor',
                'alt',
                'rot',
                'rolos_prog',
                'quilos_prog',
                'rolos_real',
                'quilos_real',
                'rolos_prod',
                'quilos_prod',
            ],
            'tec_dados': tec_dados,
        })

        tipo_tecido = ''
        for row in tec_dados:
            if not tipo_tecido:
                tipo_tecido = row['tam']
            elif tipo_tecido != row['tam']:
                tipo_tecido = 'X'

        tecido_ob = {
            'TIN': 'OB2',
            'INT': 'OB1',
            '': 'Indefinido',
        }
        try:
            tipo_ob = f"{tecido_ob[tipo_tecido]} ({tipo_tecido})"
        except KeyError:
            tipo_ob = f"Erro ({tipo_tecido})"

        self.context.update({
            'tipo_ob': tipo_ob,
        })

        if tipo_tecido == 'INT':
            self.context['headers'].append('OB2')
            self.context['fields'].append('ob2')
            for row in dados:
                if row['ob2']:
                    row['ob2|LINK'] = reverse(
                        'beneficia:ob__get',
                        args=[row['ob2']],
                    )

        elif tipo_tecido == 'TIN':
            self.context['headers'].append('OT')
            self.context['fields'].append('ot')
            for row in dados:
                if row['ot']:
                    row['ot|LINK'] = reverse(
                        'beneficia:ot__get',
                        args=[row['ot']],
                    )

        dest_dados = ob_destinos.query(self.cursor, self.context['ob'])

        dest_erro = False
        for row in dest_dados:
            if row['numero']:
                row['numero|LINK'] = reverse(
                    'beneficia:ob__get',
                    args=[row['numero']],
                )
            if row.get('op'):
                row['op|LINK'] = reverse(
                    'producao:op__get',
                    args=[row['op']],
                )
            else:
                row['op'] = '-'
            if row.get('erro'):
                dest_erro = True
            else:
                row['erro'] = '-'

        dest_headers = [
            'Número',
            'Depósito',
            'Rolos',
            'Quilos',
            'OP',
        ]
        dest_fields = [
            'numero',
            'dep',
            'rolos',
            'quilos',
            'op',
        ]
        if dest_erro:
            dest_headers.insert(1, 'Erro')
            dest_fields.insert(1, 'erro')

        totalize_data(
            dest_dados,
            {
                'sum': ['rolos', 'quilos'],
                'descr': {'numero': 'Total:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )

        self.context.update({
            'dest_headers': dest_headers,
            'dest_fields': dest_fields,
            'dest_dados': dest_dados,
        })


    def get(self, request, *args, **kwargs):
        if 'ob' in kwargs:
            return self.post(request, *args, **kwargs)
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        if 'ob' in kwargs:
            self.context['post'] = True
            self.context['form'] = self.Form_class(kwargs)
        else:
            self.context['post'] = 'busca' in self.request.POST
            self.context['form'] = self.Form_class(self.request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.mount_context()
            self.context_to_form_post()
            self.context['form'] = self.Form_class(self.context)
        return render(request, self.template_name, self.context)
