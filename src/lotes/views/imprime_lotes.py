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

    def mount_context(self, cursor, op, oc_ininial, oc_final):
        context = {}

        oc_ininial_val = oc_ininial or 0
        oc_final_val = oc_final or 99999

        # Lotes ordenados por OC
        data = models.get_imprime_lotes(
            cursor, op, oc_ininial_val, oc_final_val)
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

            impressao = models.ModeloTermica.objects.get(
                codigo='CARTELA DE LOTE')

            teg = TermalPrint()
            teg.template(impressao.modelo, '\r\n')
            teg.context(data[0])
            teg.printer_send1()

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'data' in kwargs:
            form.data['data_de'] = kwargs['data']
            form.data['data_ate'] = kwargs['data']
        if form.is_valid():
            op = form.cleaned_data['op']
            oc_ininial = form.cleaned_data['oc_ininial']
            oc_final = form.cleaned_data['oc_final']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, op, oc_ininial, oc_final))
        context['form'] = form
        return render(request, self.template_name, context)
