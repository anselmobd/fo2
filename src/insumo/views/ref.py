from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefsHpSD

import insumo.forms as forms
import insumo.queries as queries
from insumo.queries import (
    ref_parametros,
    ref_usado_em,
)


class Ref(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Ref, self).__init__(*args, **kwargs)
        self.Form_class = forms.RefForm
        self.template_name = 'insumo/ref.html'
        self.title_name = 'Insumo'
        self.get_args = ['item']

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        item = self.form.cleaned_data['item']

        self.context.update({'item': item})

        if len(item) == 5:
            data = queries.item_count_nivel(cursor, item)
            row = data[0]
            if row['COUNT'] > 1:
                self.context.update({
                    'msg_erro':
                        'Referência de insumo ambígua. Informe o nível.',
                })
                return self.context
            elif row['COUNT'] == 1:
                nivel = row['NIVEL']
                ref = item
        else:
            nivel = item[0]
            if nivel not in ('2', '9'):
                self.context.update({
                    'msg_erro': 'Nível inválido',
                })
                return self.context
            ref = item[-5:]
            data = queries.item_count_nivel(cursor, ref, nivel)
            row = data[0]
        if row['COUNT'] == 0:
            self.context.update({
                'msg_erro': 'Referência de insumo não encontrada',
            })
            return self.context
        self.context.update({
            'nivel': nivel,
            'ref': ref,
        })

        # Informações básicas
        data = queries.ref_inform(cursor, nivel, ref)
        self.context.update({
            'headers': ('Descrição', 'Unidade de medida', 'Conta de estoque',
                        'NCM', 'Código Contábil'),
            'fields': ('DESCR', 'UM', 'CONTA_ESTOQUE',
                       'NCM', 'CODIGO_CONTABIL'),
            'data': data,
        })

        if data[0]['FORNECEDOR'] is not None:
            # Informações básicas 2
            data = queries.ref_inform(cursor, nivel, ref)
            self.context.update({
                'b2_headers': ['Último fornecedor'],
                'b2_fields': ['FORNECEDOR'],
                'b2_data': data,
            })

        # Informações básicas - tecidos
        if nivel == '2':
            self.context.update({
                'm_headers': ('Linha de produto', 'Coleção',
                              'Artigo de produto', 'Tipo de produto'),
                'm_fields': ('LINHA', 'COLECAO',
                             'ARTIGO', 'TIPO_PRODUTO'),
                'm_data': data,
            })

        # Cores
        c_data = queries.ref_cores(cursor, nivel, ref)
        if len(c_data) != 0:
            self.context.update({
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
            self.context.update({
                't_headers': ('Tamanho', 'Descrição', 'Complemento'),
                't_fields': ('TAM', 'DESCR', 'COMPL'),
                't_data': t_data,
            })

        p_data = ref_parametros.query(cursor, nivel, ref)
        self.context['param'] = {
            'titulo': "Parâmetros",
            'data': p_data,
            'vazio': "Nenhum",
        }
        if p_data:
            max_digits = 0
            for row in p_data:
                num_digits = str(row['estoque_minimo'])[::-1].strip('0').find('.')
                max_digits = max(max_digits, num_digits)
                num_digits = str(row['estoque_maximo'])[::-1].strip('0').find('.')
                max_digits = max(max_digits, num_digits)
            TableDefsHpSD({
                'tam': ["Tamanho"],
                'cor': ["Cor"],
                'deposito': ["Depósito"],
                'estoque_minimo': ["Estoque mínimo", 'r', max_digits],
                'estoque_maximo': ["Estoque máximo", 'r', max_digits],
                'lead': ["Lead", 'r'],
            }).hfsd_dict(
                context=self.context['param'],
            )

        self.context['usado'] = self.get_usado(cursor, nivel, ref)

    def get_usado(self, cursor, nivel, ref):
        data = ref_usado_em.query(cursor, nivel, ref)
        result = {
            'titulo': "Utilizado nas estruturas",
            'data': data,
            'vazio': "Nenhuma",
        }
        if data:
            max_digits = 0
            for row in data:
                num_digits = str(row['consumo'])[::-1].strip('0').find('.')
                max_digits = max(max_digits, num_digits)
                if row['nivel'] == '1':
                    row['ref|LINK'] = reverse('produto:ref__get', args=[row['ref']])
                if row['nivel'] == '5':
                    row['estagio'] = '-'

            TableDefsHpSD({
                'tam_comp': ["Tamanho"],
                'cor_comp': ["Cor"],
                'tipo': ["Tipo"],
                'nivel': ["Nível"],
                'ref': ["Referência"],
                'descr': ["Descrição"],
                'tam': ["Tamanho"],
                'cor': ["Cor"],
                'alternativa': ["Alternativa", 'r'],
                'consumo': ["Consumo", 'r', max_digits],
                'estagio': ["Estágio"],
            }).hfsd_dict(
                context=result,
            )
        return result
