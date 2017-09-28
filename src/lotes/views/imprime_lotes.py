import errno
from subprocess import Popen, PIPE
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.template import Template, Context

from fo2 import settings
from utils.classes import TermalPrint

from lotes.forms import ImprimeLotesForm
import lotes.models as models


class ImprimeLotes(View):
    Form_class = ImprimeLotesForm
    template_name = 'lotes/imprime_lotes.html'
    title_name = 'Imprime cartela de lotes'

    def mount_context_and_print(self, cursor, op, tam, cor, order,
                                oc_ininial, oc_final,
                                pula, qtd_lotes, print):
        context = {}

        oc_ininial_val = oc_ininial or 0
        oc_final_val = oc_final or 99999

        # Lotes ordenados por OC
        data = models.get_imprime_lotes(
            cursor, op, tam, cor, order, oc_ininial_val, oc_final_val,
            pula, qtd_lotes)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
        else:
            context.update({
                'op': op,
                'oc_ininial': oc_ininial,
                'oc_final': oc_final,
                'count': len(data),
            })
            for row in data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
            context.update({
                'headers': ('Referência', 'Tamanho', 'Cor',
                            'Estágio', 'Período', 'OC', 'Quant.', 'Lote'),
                'fields': ('REF', 'TAM', 'COR',
                           'EST', 'PERIODO', 'OC', 'QTD', 'LOTE'),
                'data': data,
            })

            if print:
                impressao = models.ModeloTermica.objects.get(
                    codigo='CARTELA DE LOTE')

                teg = TermalPrint()
                teg.template(impressao.modelo, '\r\n')
                teg.printer_init()
                try:
                    for row in data:
                        row['op'] = '{:09}'.format(row['OP'])
                        row['periodo'] = '{}'.format(row['PERIODO'])
                        row['oc'] = '{:05}'.format(row['OC'])
                        row['lote'] = '{}'.format(row['LOTE'])
                        row['ref'] = row['REF']
                        row['tam'] = row['TAM']
                        row['cor'] = row['COR']
                        row['narrativa'] = row['NARRATIVA']
                        row['qtd'] = row['QTD']
                        row['divisao'] = '{:04}'.format(row['DIVISAO'])
                        row['descricao_divisao'] = row['DESCRICAO_DIVISAO']
                        teg.context(row)
                        teg.printer_send()
                finally:
                    teg.printer_end()

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            order = form.cleaned_data['order']
            oc_ininial = form.cleaned_data['oc_ininial']
            oc_final = form.cleaned_data['oc_final']
            pula = form.cleaned_data['pula']
            qtd_lotes = form.cleaned_data['qtd_lotes']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, order, oc_ininial, oc_final,
                    pula, qtd_lotes, 'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
