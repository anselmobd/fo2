from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefsH, TableDefsHpSD
from utils.functions.dictlist.get_max_digits import get_max_digits
from utils.functions.models.dictlist import dictlist_to_lower

from produto.queries import prod_tamanhos

import insumo.forms as forms
import insumo.queries as queries
from insumo.queries import (
    item_count_nivel,
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

        if len(item) not in (5, 6):
            self.context.update({
                'msg_erro':
                    'Informe "Referência" ou "NívelReferência".',
            })
            return

        if len(item) == 5:
            nivel = None
            ref = item
        else:
            nivel = item[0]
            ref = item[1:]
            if nivel not in ('2', '9'):
                self.context['msg_erro'] = 'Nível inválido'
                return

        data = item_count_nivel.query(cursor, ref, nivel)

        if not data:
            self.context.update({
                'msg_erro': 'Referência de insumo não encontrada',
            })
            return
    
        if data[0]['count'] != 1:
            self.context.update({
                'msg_erro':
                    'Referência de insumo não encontrada ou ambígua.',
            })
            return

        nivel = data[0]['nivel']
        self.context.update({
            'nivel': nivel,
            'ref': ref,
        })

        self.context['infos'] = self.get_infos(cursor, nivel, ref)
        self.context['cores'] = self.get_cores(cursor, nivel, ref)
        self.context['taman'] = self.get_taman(cursor, nivel, ref)
        self.context['param'] = self.get_param(cursor, nivel, ref)
        self.context['usado'] = self.get_usado(cursor, nivel, ref)

    def get_infos(self, cursor, nivel, ref):
        data = dictlist_to_lower(
            queries.ref_inform(cursor, nivel, ref))
        result = {
            'data': data,
        }
        if data:
            result['info1'] = TableDefsH({
                'descr': ["Descrição"],
                'um': ["Unidade de medida"],
                'conta_estoque': ["Conta de estoque"],
                'ncm': ["NCM"],
                'codigo_contabil': ["Código Contábil"],
            }).hfs_dict()

            if data[0]['fornecedor'] is not None:
                result['info2'] = TableDefsH({
                    'fornecedor': ["Último fornecedor"],
                }).hfs_dict()
    
            if nivel == '2':
                result['info3'] = TableDefsH({
                    'linha': ["Linha de produto"],
                    'colecao': ["Coleção"],
                    'artigo': ["Artigo de produto"],
                    'tipo_produto': ["Tipo de produto"],
                }).hfs_dict()

        return result

    def get_cores(self, cursor, nivel, ref):
        data = dictlist_to_lower(
            queries.ref_cores(cursor, nivel, ref))
        result = {
            'titulo': "Cores",
            'data': data,
        }
        if data:
            TableDefsH({
                'cor': ["Cor"],
                'descr': ["Descrição"],
            }).hfs_dict(context=result)
        return result

    def get_taman(self, cursor, nivel, ref):
        data = dictlist_to_lower(prod_tamanhos(cursor, nivel, ref))
        result = {
            'titulo': "Tamanhos",
            'data': data,
        }
        if data:
            for row in data:
                if row['compl'] is None:
                    row['compl'] = '-'
            TableDefsH({
                'tam': ["Tamanho"],
                'descr': ["Descrição"],
                'compl': ["Complemento"],
            }).hfs_dict(context=result)
        return result

    def get_param(self, cursor, nivel, ref):
        data = ref_parametros.query(cursor, nivel, ref)
        result = {
            'titulo': "Parâmetros",
            'data': data,
            'vazio': "Nenhum",
        }
        if data:
            max_digits = max(
                get_max_digits(
                    data,
                    'estoque_minimo',
                    'estoque_maximo'
                )
            )
            TableDefsHpSD({
                'tam': ["Tamanho"],
                'cor': ["Cor"],
                'deposito': ["Depósito"],
                'estoque_minimo': ["Estoque mínimo", 'r', max_digits],
                'estoque_maximo': ["Estoque máximo", 'r', max_digits],
                'lead': ["Lead", 'r'],
            }).hfsd_dict(context=result)
        return result

    def get_usado(self, cursor, nivel, ref):
        data = ref_usado_em.query(cursor, nivel, ref)
        result = {
            'titulo': "Utilizado nas estruturas",
            'data': data,
            'vazio': "Nenhuma",
        }
        if data:
            max_digits = get_max_digits(
                data,
                'consumo',
            )
            for row in data:
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
            }).hfsd_dict(context=result)
        return result
