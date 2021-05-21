from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

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

        caixa_op = 0
        cor_ant = '!!!!!!'
        tam_ant = '!!!!'
        for lote in data:
            lote['lote'] = f"{lote['periodo']}{lote['oc']:05}"
            lote['lote|LINK'] = reverse('producao:posicao__get', args=[lote['lote']])
            lote['peso'] = " "

            if lote['cor'] != cor_ant or lote['tam'] != tam_ant:
                cor_ant = lote['cor']
                tam_ant = lote['tam']
                caixa_ct = 1
                caixa_op += 1
                conta_lotes_caixa = 1
                qtd_caixa = 0
            else:
                conta_lotes_caixa += 1

            if conta_lotes_caixa > rc.lotes_caixa:
                conta_lotes_caixa = 1
                caixa_ct += 1
                caixa_op += 1
                qtd_caixa = lote['qtd']
            else:
                qtd_caixa += lote['qtd']

            lote['qtd_caixa'] = qtd_caixa
            lote['caixa_op'] = caixa_op
            lote['caixa_ct'] = caixa_ct

        caixa_op_ant = 0
        cor_ant = '!!!!!!'
        tam_ant = '!!!!'
        total_cx_op = data[-1]['caixa_op']
        for lote in data[::-1]:
            if lote['caixa_op'] != caixa_op_ant:
                caixa_op_ant = lote['caixa_op']
                qtd_caixa = lote['qtd_caixa']
            else:
                lote['qtd_caixa'] = qtd_caixa

            if lote['cor'] != cor_ant or lote['tam'] != tam_ant:
                cor_ant = lote['cor']
                tam_ant = lote['tam']
                total_cx_ct = lote['caixa_ct']

            lote['num_caixa_txt'] = f"{lote['caixa_op']}/{total_cx_op}"
            lote['cor_tam_caixa_txt'] = f"{lote['caixa_ct']}/{total_cx_ct}"

        # caixas = lotes.classes.CaixasDeLotes(data, rc.lotes_caixa)
        # c_data = caixas.as_data()

        totalize_grouped_data(data, {
            'group': ['cor'],
            'sum': ['qtd'],
            'count': [],
            'descr': {'op': 'Cor'},
            'global_sum': ['qtd'],
            'global_descr': {'op': 'Total'},
            'empty': '-',
            'clean_pipe': True,
        })
        group = ['op', 'ref', 'num_caixa_txt',
                    'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa']
        group_rowspan(data, group)
        context.update({
            'headers': ('OP', 'Referência', 'Cx.OP',
                        'Cor', 'Tamanho', 'Cx.C/T', 'Peças',
                        'Lote', 'Quant.', 'Peso'),
            'fields': ('op', 'ref', 'num_caixa_txt',
                        'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa',
                        'lote', 'qtd', 'peso'),
            'group': group,
            'data': data,
        })

        return

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
