from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

import lotes.classes
import lotes.queries
from lotes.forms import OpForm


class OpCaixa(View):
    Form_class = OpForm
    template_name = 'lotes/op_caixa.html'
    title_name = 'Lista caixas de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        data_op = lotes.queries.op.op_inform(cursor, op, cached=False)
        if len(data_op) == 0:
            context.update({
                'msg_erro': 'OP não encontrada',
            })
            return context

        row_op = data_op[0]
        context.update({
            'ref': row_op['REF'],
            'tipo_ref': row_op['TIPO_REF'],
            'colecao': row_op['COLECAO'],
        })

        if context['tipo_ref'] not in ['MD', 'MP']:
            context.update({
                'msg_erro': 'Lotes agrupados em caixas é utilizado apenas para MD e MP',
            })
            return context

        # Lotes order 'r' = referência + cor + tamanho + OC
        data = lotes.queries.lote.get_imprime_lotes(cursor, op=op, order='r')
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontrados',
            })
            return context

        try:
            rc = lotes.models.RegraColecao.objects_referencia.get(
                colecao=data[0]['colecao'], referencia=context['ref'][0])
            context.update({
                'ini_ref': rc.referencia,
            })
        except lotes.models.RegraColecao.DoesNotExist:
            try:
                rc = lotes.models.RegraColecao.objects.get(
                    colecao=data[0]['colecao'])
                context.update({
                    'ini_ref': '',
                })
            except lotes.models.RegraColecao.DoesNotExist:
                self.context.update({
                    'msg_erro': 'Regra de coleção e referência não encontrados',
                })
                return
        context.update({
            'lotes_caixa': rc.lotes_caixa,
        })

        caixas = lotes.classes.CaixasDeLotes(data, rc.lotes_caixa)
        c_data = caixas.as_data()

        group = ['op', 'ref', 'num_caixa_txt',
                    'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa']
        group_rowspan(c_data, group)
        context.update({
            'headers': ('OP', 'Referência', 'Cx.OP',
                        'Cor', 'Tamanho', 'Cx.C/T', 'Peças',
                        'Lote', 'Quant.', 'Peso'),
            'fields': ('op', 'ref', 'num_caixa_txt',
                        'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa',
                        'lote', 'qtd', 'peso'),
            'group': group,
            'data': c_data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
