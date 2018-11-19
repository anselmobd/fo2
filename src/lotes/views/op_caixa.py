from operator import itemgetter

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import OpForm
import lotes.models as models


class CaixasDeLotes:

    def __init__(self, lotes, lotes_por_caixa):
        self.lotes_por_caixa = lotes_por_caixa
        self.op = lotes[0]['op']
        self.ref = lotes[0]['ref']
        self.periodo = lotes[0]['periodo']

        self.caixas = {}
        self.qtd_caixas = 0

        self.add_lotes(lotes)

    def add_lotes(self, lotes):
        for lote in lotes:
            self.add_lote(lote)

    def add_lote(self, lote):
        refcortam = self.pick_refcortam_with_open_caixa(
            lote['cor'], lote['ordem_tamanho'], lote['tam'])
        refcortam['caixas'][-1]['lotes'].append(
          {
            'periodo': lote['periodo'],
            'oc': lote['oc'],
            'qtd': lote['qtd'],
          }
        )

    def pick_refcortam_with_open_caixa(self, cor, ord_tam, tam):
        refcortam = self.pick_refcortam(cor, ord_tam, tam)
        if len(refcortam['caixas']) == 0 or \
                len(refcortam['caixas'][-1]['lotes']) == self.lotes_por_caixa:
            refcortam['caixas'].append(self.create_caixa())
        return refcortam

    def pick_refcortam(self, cor, ord_tam, tam):
        if cor not in self.caixas.keys():
            self.caixas[cor] = {}
        if ord_tam not in self.caixas[cor].keys():
            self.caixas[cor][ord_tam] = {
                'tam': tam,
                'caixas': [],
            }
        return(self.caixas[cor][ord_tam])

    def create_caixa(self):
        self.qtd_caixas += 1
        return {'id_caixa': self.qtd_caixas,
                'lotes': []
                }

    def as_data(self):
        data = []
        total_pecas = 0
        for cor in sorted(self.caixas):
            total_pecas_cor = 0
            for ord_tam in self.caixas[cor]:
                for idx_caixa, caixa in enumerate(
                        self.caixas[cor][ord_tam]['caixas']):
                    for lote in caixa['lotes']:
                        lote_num = '{}{:05}'.format(
                            lote['periodo'], lote['oc'])
                        total_pecas += lote['qtd']
                        total_pecas_cor += lote['qtd']
                        row = {
                            'op': self.op,
                            'ref': self.ref,
                            'num_caixa_txt': '{}/{}'.format(
                                caixa['id_caixa'], self.qtd_caixas),
                            'cor': cor,
                            'tam': self.caixas[cor][ord_tam]['tam'],
                            'cor_tam_caixa_txt': '{}/{}'.format(
                                idx_caixa+1, len(
                                    self.caixas[cor][ord_tam]['caixas'])),
                            'qtd_caixa': sum(
                                item['qtd'] for item in caixa['lotes']),
                            'lote': lote_num,
                            'lote|LINK': '/lotes/posicao/{}'.format(lote_num),
                            'qtd': lote['qtd'],
                            'peso': ' ',
                        }
                        data.append(row)
            row = {
                'op': 'Cor',
                'ref': '-',
                'num_caixa_txt': '-',
                'cor': cor,
                'tam': '-',
                'cor_tam_caixa_txt': '-',
                'qtd_caixa': total_pecas_cor,
                'lote': '-',
                'lote|LINK': '',
                'qtd': '-',
                'peso': '-',
            }
            data.append(row)
        row = {
            'op': 'Total',
            'ref': '-',
            'num_caixa_txt': '-',
            'cor': '-',
            'tam': '-',
            'cor_tam_caixa_txt': '-',
            'qtd_caixa': total_pecas,
            'lote': '-',
            'lote|LINK': '',
            'qtd': '-',
            'peso': '-',
        }
        data.append(row)
        return data


class OpCaixa(View):
    Form_class = OpForm
    template_name = 'lotes/op_caixa.html'
    title_name = 'Lista caixas de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        data = models.get_imprime_lotes(cursor, op=op, order='r')
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontradas',
            })
        else:
            if data[0]['colecao'] == 5:  # camisa
                lotes_por_caixa = 2
            else:
                lotes_por_caixa = 3

            caixas = CaixasDeLotes(data, lotes_por_caixa)
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
