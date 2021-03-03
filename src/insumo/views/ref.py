from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import insumo.forms as forms
import insumo.queries as queries


class Ref(View):
    Form_class = forms.RefForm
    template_name = 'insumo/ref.html'
    title_name = 'Insumo'

    def mount_context(self, cursor, item):
        context = {'item': item}

        if len(item) == 5:
            data = queries.item_count_nivel(cursor, item)
            row = data[0]
            if row['COUNT'] > 1:
                context.update({
                    'msg_erro':
                        'Referência de insumo ambígua. Informe o nível.',
                })
                return context
            elif row['COUNT'] == 1:
                nivel = row['NIVEL']
                ref = item
        else:
            nivel = item[0]
            if nivel not in ('2', '9'):
                context.update({
                    'msg_erro': 'Nível inválido',
                })
                return context
            ref = item[-5:]
            data = queries.item_count_nivel(cursor, ref, nivel)
            row = data[0]
        if row['COUNT'] == 0:
            context.update({
                'msg_erro': 'Referência de insumo não encontrada',
            })
            return context
        context.update({
            'nivel': nivel,
            'ref': ref,
        })

        # Informações básicas
        data = queries.ref_inform(cursor, nivel, ref)
        context.update({
            'headers': ('Descrição', 'Unidade de medida', 'Conta de estoque',
                        'NCM', 'Código Contábil'),
            'fields': ('DESCR', 'UM', 'CONTA_ESTOQUE',
                       'NCM', 'CODIGO_CONTABIL'),
            'data': data,
        })

        if data[0]['FORNECEDOR'] is not None:
            # Informações básicas 2
            data = queries.ref_inform(cursor, nivel, ref)
            context.update({
                'b2_headers': ['Último fornecedor'],
                'b2_fields': ['FORNECEDOR'],
                'b2_data': data,
            })

        # Informações básicas - tecidos
        if nivel == '2':
            context.update({
                'm_headers': ('Linha de produto', 'Coleção',
                              'Artigo de produto', 'Tipo de produto'),
                'm_fields': ('LINHA', 'COLECAO',
                             'ARTIGO', 'TIPO_PRODUTO'),
                'm_data': data,
            })

        # Cores
        c_data = queries.ref_cores(cursor, nivel, ref)
        if len(c_data) != 0:
            context.update({
                'c_headers': ('Cor', 'Descrição'),
                'c_fields': ('COR', 'DESCR'),
                'c_data': c_data,
            })

        # Tamanhos
        t_data = queries.ref_tamanhos(cursor, nivel, ref)
        for row in t_data:
            if row['COMPL'] is None:
                row['COMPL'] = '-'
        if len(t_data) != 0:
            context.update({
                't_headers': ('Tamanho', 'Descrição', 'Complemento'),
                't_fields': ('TAM', 'DESCR', 'COMPL'),
                't_data': t_data,
            })

        # Parametros
        p_data = queries.ref_parametros(cursor, nivel, ref)
        if len(p_data) != 0:
            context.update({
                'p_headers': ('Tamanho', 'Cor', 'Depósito', 'Estoque mínimo',
                              'Estoque máximo', 'Lead'),
                'p_fields': ('TAM', 'COR', 'DEPOSITO', 'ESTOQUE_MINIMO',
                             'ESTOQUE_MAXIMO', 'LEAD'),
                'p_data': p_data,
            })

        # Usado em
        u_data = queries.ref_usado_em(cursor, nivel, ref)
        u_link = ('REF')
        for row in u_data:
            if row['NIVEL'] == '1':
                row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
            if row['NIVEL'] == '5':
                row['ESTAGIO'] = '-'
        if len(u_data) != 0:
            context.update({
                'u_headers': ('Tamanho', 'Cor',
                              'Tipo', 'Nível', 'Referência', 'Descrição',
                              'Tamanho', 'Cor',
                              'Alternativa', 'Consumo', 'Estágio'),
                'u_fields': ('TAM_COMP', 'COR_COMP',
                             'TIPO', 'NIVEL', 'REF', 'DESCR',
                             'TAM', 'COR',
                             'ALTERNATIVA', 'CONSUMO', 'ESTAGIO'),
                'u_data': u_data,
                'u_link': u_link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'item' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'item' in kwargs:
            form.data['item'] = kwargs['item']
        if form.is_valid():
            item = form.cleaned_data['item']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, item))
        context['form'] = form
        return render(request, self.template_name, context)
