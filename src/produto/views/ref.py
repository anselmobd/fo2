import re
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.views import group_rowspan

import produto.forms as forms
import produto.queries as queries
import produto.models as models


class Ref(View):
    Form_class = forms.ReferenciaForm
    template_name = 'produto/ref.html'
    title_name = 'Produto'

    def mount_context(self, request, cursor, ref):
        context = {'ref': ref}

        if len(ref) != 5:
            context.update({
                'msg_erro': 'Código de referência inválido',
            })
            return context

        # Informações básicas
        data = queries.ref_inform(cursor, ref)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Referência não encontrada',
            })
        else:
            try:
                fichas = models.FichaTecnica.objects.filter(
                    referencia=ref, habilitada=True
                ).order_by('tipo')
                ftecs = []
                for ficha in fichas:
                    ftecs.append({
                        'tipo': ficha.tipo,
                        'link': f'/media/{ficha.ficha}',
                    })
                context.update({
                    'ftecs': ftecs,
                })

            except models.FichaTecnica.DoesNotExist:
                pass
            
            modelo_link = \
                '<a href="{modelo_link}">{modelo}&nbsp;' \
                '<span class="glyphicon glyphicon-link" ' \
                'aria-hidden="true"></span></a>'.format(
                    modelo_link=reverse(
                        'produto:modelo__get', args=[data[0]['MODELO']]),
                    modelo=data[0]['MODELO'])
            if data[0]['MODELO'] != ' ':
                context.update({'modelo': modelo_link})
            context.update({
                'tipo': data[0]['TIPO'],
            })

            if data[0]['NUMERO_MOLDE'] is None:
                data[0]['NUMERO_MOLDE'] = '-'

            context.update({
                'headers': ('Descrição', 'Conta de estoque',
                            'Artigo', 'Linha', 'Coleção', 'Modelagem'),
                'fields': ('DESCR', 'CONTA_ESTOQUE',
                           'ARTIGO', 'LINHA', 'COLECAO', 'NUMERO_MOLDE'),
                'data': data,
            })

            for row in data:
                if row['COLECAO_CLIENTE'] is None:
                    row['COLECAO_CLIENTE'] = '-'
                if row['STATUS'] is None:
                    row['STATUS'] = '-'
                if row['CNPJ9'] is None:
                    row['CLIENTE'] = '-'
                else:
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['CLIENTE'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers2': ('Coleção', 'Cliente', 'NCM',
                             'Status (Responsável)'),
                'fields2': ('COLECAO_CLIENTE', 'CLIENTE', 'NCM', 'STATUS'),
                'data2': data,
            })

            # PAs
            pa_data = queries.ref_utilizada_em(cursor, ref)
            pa_link = ('REF')
            for row in pa_data:
                if row['RESPONSAVEL'] is None:
                    row['RESPONSAVEL'] = '-'
                if row['REF'] != ' ':
                    row['LINK'] = reverse(
                        'produto:ref__get', args=[row['REF']])
            if len(pa_data) != 0:
                context.update({
                    'pa_headers': ('Tipo', 'Referência', 'Alternativa',
                                   'Responsável'),
                    'pa_fields': ('TIPO', 'REF', 'ALTERNATIVA', 'RESPONSAVEL'),
                    'pa_data': pa_data,
                    'pa_link': pa_link,
                })

            # Cores
            c_data = queries.ref_cores(cursor, ref)
            cores = ', '.join([data['COR'] for data in c_data])
            if len(c_data) != 0:
                context.update({
                    'c_headers': ('Cor', 'Descrição'),
                    'c_fields': ('COR', 'DESCR'),
                    'c_data': c_data,
                })

            # Tamanhos
            t_data = queries.ref_tamanhos(cursor, ref)
            if len(t_data) != 0:
                context.update({
                    't_headers': ('Tamanho', 'Descrição', 'Peças no lote'),
                    't_fields': ('TAM', 'DESCR', 'LOTE_PECAS'),
                    't_data': t_data,
                })

            # Estruturas
            e_data = queries.ref_estruturas(cursor, ref)
            conta_ref = 0
            conta_tam_cor = 0
            for row in e_data:
                row['ALT'] = '{} ({})'.format(
                    row['ALTERNATIVA'], row['DESCR'])
                if row['TAM'] != '000' or row['COR'] != '000000':
                    conta_tam_cor += 1
                if row['REF'] != '-':
                    ref_list = list(set(row['REF'].split(', ')))
                    row['REF'] = ', '.join(ref_list)
                    conta_ref += 1
                    row['REF'] = re.sub(
                        r'([A-Z0-9]+)',
                        r'<a href="'+reverse(
                            'produto:ref'
                        )+r'\1">\1&nbsp;<span '
                        'class="glyphicon glyphicon-link" '
                        'aria-hidden="true"></span></a>',
                        row['REF'])

            e_headers = ['Alternativa']
            e_fields = ['ALT']
            if conta_ref != 0:
                e_headers.append('Componente produto')
                e_fields.append('REF')
            if conta_tam_cor != 0:
                e_headers.extend(['Tamanho', 'Cor'])
                e_fields.extend(['TAM', 'COR'])

            if len(e_data) != 0:
                context.update({
                    'e_headers': e_headers,
                    'e_fields': e_fields,
                    'e_data': e_data,
                    'e_safe': ('REF',),
                })

            # Roteiros
            r_data = queries.ref_roteiros(cursor, ref)

            conta_tam_cor = 0
            for row in r_data:
                if row['TAM'] != '000' or row['COR'] != '000000':
                    conta_tam_cor += 1

            r_headers = ['Alternativa', 'Roteiro']
            r_fields = ['ALTERNATIVA', 'ROTEIRO']
            if conta_tam_cor != 0:
                r_headers.extend(['Tamanho', 'Cor'])
                r_fields.extend(['TAM', 'COR'])

            if len(r_data) != 0:
                context.update({
                    'r_headers': r_headers,
                    'r_fields': r_fields,
                    'r_data': r_data,
                })
            if has_permission(request, 'base.can_generate_product_stages'):
                context.update({
                    'gera_roteiros_link': reverse(
                        'produto:gera_roteiros_padrao_ref', args=[ref, 1])

                })

            # Detalhando Roteiros
            roteiros = []
            for row in r_data:
                roteiro_tit = {
                    'alternativa': row['ALTERNATIVA'],
                    'roteiro': row['ROTEIRO'],
                    'tamanho': row['TAM'],
                    'cor': row['COR'],
                }
                roteiro = queries.ref_1roteiro(
                    cursor, ref, row['NUMERO_ALTERNATI'],
                    row['NUMERO_ROTEIRO'], row['TAM'], row['COR'])
                inserir = True
                for roteiro1 in roteiros:
                    if roteiro1['r_data'] == roteiro:
                        roteiro1['r_titulos'].append(roteiro_tit)
                        inserir = False
                if inserir:
                    roteiros.append({
                        'r_titulos': [roteiro_tit],
                        'r_headers': ['Sequência', 'Operação', 'Estágio',
                                      'Gargalo'],
                        'r_fields': ['SEQ', 'OPERACAO', 'ESTAGIO', 'GARGALO'],
                        'r_data': roteiro,
                    })
            context.update({
                'roteiros': roteiros,
            })

            estr_data = []
            for row in e_data:
                if not next((estr for estr in estr_data
                             if estr["ALTERNATIVA"] == row["ALTERNATIVA"]),
                            False):
                    estr_data.append(row)

            # Detalhando Estruturas
            estruts = []
            for row in estr_data:
                if row['ALTERNATIVA'] in \
                        [r['NUMERO_ALTERNATI'] for r in r_data]:
                    estrutura = queries.ref_estrutura_comp(
                        cursor, ref, row['ALTERNATIVA'])
                    e_link = ('REF')
                    dif_000000 = 0
                    for e_row in estrutura:
                        if e_row['COR_REF'] == cores:
                            e_row['COR_REF'] = '000000'
                        if e_row['COR_REF'] != '000000':
                            dif_000000 += 1
                        if e_row['NIVEL'] == '1':
                            e_row['REF|LINK'] = reverse(
                                'produto:ref__get', args=[e_row['REF']])
                        else:
                            e_row['REF|LINK'] = reverse(
                                'insumo:ref__get',
                                args=[e_row['NIVEL']+e_row['REF']])

                    e_headers = ['Sequência', 'Nível', 'Referência',
                                 'Descrição', 'Tamanho', 'Cor',
                                 'Alternativa', 'Consumo', 'Estágio']
                    e_fields = ['SEQUENCIA', 'NIVEL', 'REF',
                                'DESCR', 'TAM_DESCR', 'COR',
                                'ALTERN', 'CONSUMO', 'ESTAGIO']
                    e_group = ['SEQUENCIA', 'NIVEL', 'REF', 'DESCR', 'TAM_DESCR',
                               'ALTERN', 'CONSUMO', 'ESTAGIO']

                    if dif_000000 != 0:
                        e_headers.insert(0, 'Cor Alternativa')
                        e_fields.insert(0, 'COR_REF')
                        e_group.insert(0, 'COR_REF')

                    group_rowspan(estrutura, e_group)

                    estruts.append({
                        'alt': '{}-{}'.format(
                            row['ALTERNATIVA'], row['DESCR']),
                        'e_headers': e_headers,
                        'e_fields': e_fields,
                        'e_data': estrutura,
                        'e_link': e_link,
                        'e_group': e_group,
                    })

            context.update({
                'estruts': estruts,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'ref' in kwargs:
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
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(request, cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)
