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

    def mount_context(self, cursor, estagio):
        context = {'estagio': estagio}

        if estagio == '0':
            data = models.totais_estagios(cursor)
        else:
            data = models.quant_estagio(cursor, estagio)
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
                'headers': ('Estágio', 'Lotes PA', 'Peças PA',
                            'Lotes PG', 'Peças PG',
                            'Lotes PB', 'Peças PB',
                            'Lotes MD*', 'Peças MD*',
                            'Lotes*', 'Peças'),
                'fields': ('ESTAGIO', 'LOTES_PA', 'QUANT_PA',
                           'LOTES_PG', 'QUANT_PG',
                           'LOTES_PB', 'QUANT_PB',
                           'LOTES_MD', 'QUANT_MD',
                           'LOTES', 'QUANT'),
                'data': data,
                'style': {2: 'text-align: right;',
                          3: 'text-align: right;',
                          4: 'text-align: right;',
                          5: 'text-align: right;',
                          6: 'text-align: right;',
                          7: 'text-align: right;',
                          8: 'text-align: right;',
                          9: 'text-align: right;',
                          10: 'text-align: right; font-weight: bold;',
                          11: 'text-align: right; font-weight: bold;'},
            })
        else:
            context.update({
                'headers': ('Produto', 'Tamanho', 'Cor', 'Quantidade'),
                'fields': ('REF', 'TAM', 'COR', 'QUANT'),
                'data': data,
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, estagio))
        context['form'] = form
        return render(request, self.template_name, context)
