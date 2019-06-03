from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

import lotes.forms as forms
import lotes.models as models


class QuantEstagio(View):
    Form_class = forms.QuantEstagioForm
    template_name = 'lotes/quant_estagio.html'
    title_name = 'Quantidades por estágio'

    def mount_context(self, cursor, estagio, ref):
        context = {
            'estagio': estagio,
            'ref': ref,
        }

        if estagio == '0':
            data = models.totais_estagios(cursor)
        else:
            data = models.quant_estagio(cursor, estagio, ref)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produtos no estágio',
            })
            return context

        if estagio == '0':
            total = data[0].copy()
            total['ESTAGIO'] = 'Total:'
            total['|STYLE'] = 'font-weight: bold;'
            quant_fileds = [
                'LOTES_PA', 'QUANT_PA',
                'LOTES_PG', 'QUANT_PG',
                'LOTES_PB', 'QUANT_PB',
                'LOTES_MD', 'QUANT_MD',
                'LOTES', 'QUANT']
            for field in quant_fileds:
                total[field] = 0
            for row in data:
                for field in quant_fileds:
                    total[field] += row[field]
            data.append(total)
            context.update({
                'headers': ('Estágio', 'Lotes PA', 'Lotes PG',
                            'Lotes PB', 'Lotes MD*', 'Lotes*',
                            'Peças PA', 'Peças PG', 'Peças PB',
                            'Peças MD*', 'Peças'),
                'fields': ('ESTAGIO', 'LOTES_PA', 'LOTES_PG',
                           'LOTES_PB', 'LOTES_MD', 'LOTES',
                           'QUANT_PA', 'QUANT_PG', 'QUANT_PB',
                           'QUANT_MD', 'QUANT'),
                'data': data,
                'style': {2: 'text-align: right;',
                          3: 'text-align: right;',
                          4: 'text-align: right;',
                          5: 'text-align: right;',
                          6: 'text-align: right; font-weight: bold;',
                          7: 'text-align: right;',
                          8: 'text-align: right;',
                          9: 'text-align: right;',
                          10: 'text-align: right;',
                          11: 'text-align: right; font-weight: bold;'},
            })
        else:
            total = data[0].copy()
            total['REF'] = ''
            total['TAM'] = ''
            total['COR'] = 'Total:'
            total['|STYLE'] = 'font-weight: bold;'
            quant_fileds = ['LOTES', 'QUANT']
            for field in quant_fileds:
                total[field] = 0
            for row in data:
                for field in quant_fileds:
                    total[field] += row[field]
            data.append(total)
            context.update({
                'headers': ('Produto', 'Tamanho', 'Cor', 'Lotes', 'Peças'),
                'fields': ('REF', 'TAM', 'COR', 'LOTES', 'QUANT'),
                'data': data,
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'estagio' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'estagio' in kwargs:
            form.data['estagio'] = kwargs['estagio']
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, estagio, ref))
        context['form'] = form
        return render(request, self.template_name, context)
