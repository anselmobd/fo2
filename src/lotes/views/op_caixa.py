from operator import itemgetter

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan
from utils.views import totalize_data

from lotes.forms import OpForm
import lotes.models as models


class OpCaixa(View):
    Form_class = OpForm
    template_name = 'lotes/op_caixa.html'
    title_name = 'Caixas de Ordem de Produção'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        data = models.get_imprime_lotes(
            cursor, op, None, None, 'c', None, None, None, None)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontradas',
            })
        else:

            tot_caixas = 1
            qtd_caixa = 0
            qtd_total = 0
            cor = data[0]['cor']
            tam = data[0]['tam']
            index_caixas = 0
            cor_tam_caixas = 1
            qtd_cor = 0
            totalizadores = []
            totalizador_filler = {
                'ref': '-',
                'tam': '-',
                'num_caixa_txt': '-',
                'cor_tam_caixa_txt': '-',
                'lote': '-',
                'qtd': '-'}
            for index, row in enumerate(data):
                row['lote_num'] = index+1

                trocou_cor = cor != row['cor']
                trocou_tam = tam != row['tam']
                trocou_cortam = trocou_cor or trocou_tam

                if trocou_cor:
                    dict_totalizador = {
                        'lote_num': row['lote_num']-0.5,
                        'op': 'Total',
                        'cor': cor,
                        'qtd_caixa': qtd_cor,
                        }
                    dict_totalizador.update(totalizador_filler)
                    totalizadores.extend([dict_totalizador])
                    qtd_cor = 0

                if trocou_cortam:
                    cor = row['cor']
                    tam = row['tam']
                    index_caixas = 0
                    cor_tam_caixas = 0
                else:
                    index_caixas += 1

                if trocou_cortam or index_caixas % 3 == 0:
                    cor_tam_caixas += 1
                    tot_caixas += 1
                    qtd_caixa = row['qtd']
                else:
                    qtd_caixa += row['qtd']

                row['cor_tam_caixa'] = cor_tam_caixas
                row['num_caixa'] = tot_caixas
                row['qtd_caixa'] = qtd_caixa

                qtd_cor += row['qtd']
                qtd_total += row['qtd']

                row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
                row['lote|LINK'] = '/lotes/posicao/{}'.format(row['lote'])

            dict_totalizador = {
                'lote_num': row['lote_num']+0.5,
                'op': 'Total',
                'cor': cor,
                'qtd_caixa': qtd_cor,
                }
            dict_totalizador.update(totalizador_filler)
            totalizadores.extend([dict_totalizador])

            dict_totalizador = {
                'lote_num': row['lote_num']+1,
                'op': 'Total',
                'cor': '-',
                'qtd_caixa': qtd_total,
                }
            dict_totalizador.update(totalizador_filler)
            totalizadores.extend([dict_totalizador])

            tot_caixas = row['num_caixa']
            num_caixa = 0
            tot_ct_caixas = None
            qtd_caixa = 0
            cor = ''
            tam = ''
            for row in reversed(data):
                row['num_caixa_txt'] = '{}/{}'.format(
                    row['num_caixa'], tot_caixas)

                trocou_cortam = cor != row['cor'] or tam != row['tam']
                if trocou_cortam:
                    cor = row['cor']
                    tam = row['tam']
                    tot_ct_caixas = row['cor_tam_caixa']

                if num_caixa != row['num_caixa']:
                    num_caixa = row['num_caixa']
                    qtd_caixa = row['qtd_caixa']
                else:
                    row['qtd_caixa'] = qtd_caixa

                row['cor_tam_caixa_txt'] = '{}/{}'.format(
                    row['cor_tam_caixa'], tot_ct_caixas)

            for totalizador in totalizadores:
                data.append(totalizador)
            data.sort(key=itemgetter('lote_num'))

            group = ['op', 'ref', 'num_caixa_txt',
                     'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa']
            group_rowspan(data, group)
            context.update({
                'headers': ('OP', 'Referência', 'Cx.OP',
                            'Cor', 'Tamanho', 'Cx.C/T', 'Qtd.Cx.',
                            'Lote', 'Quant.'),
                'fields': ('op', 'ref', 'num_caixa_txt',
                           'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa',
                           'lote', 'qtd'),
                'group': group,
                'data': data,
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
