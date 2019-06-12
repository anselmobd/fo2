from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

import lotes.forms as forms
import lotes.models as models


class TotalEstagio(View):
    Form_class = forms.TotaisEstagioForm
    template_name = 'lotes/total_estagio.html'
    title_name = 'Quantidades por estágio'

    def mount_context(self, cursor, tipo_roteiro):
        context = {
            'tipo_roteiro': tipo_roteiro,
        }

        data = models.totais_estagios(cursor, tipo_roteiro)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem quantidades',
            })
            return context

        total_liberado = data[0].copy()
        total_liberado[
            'ESTAGIO'] = 'Total em produção (apenas após 3 - PCP - LIBERACAO):'
        total_liberado['|STYLE'] = 'font-weight: bold;'
        total_geral = data[0].copy()
        total_geral['ESTAGIO'] = 'Total geral (incluindo 3 - PCP - LIBERACAO):'
        quant_fields = [
            'LOTES_PA', 'QUANT_PA',
            'LOTES_PG', 'QUANT_PG',
            'LOTES_PB', 'QUANT_PB',
            'LOTES_MD', 'QUANT_MD',
            'LOTES', 'QUANT']
        for field in quant_fields:
            total_geral[field] = 0
            total_liberado[field] = 0
        for row in data:
            for field in quant_fields:
                total_geral[field] += row[field]
            if row['CODIGO_ESTAGIO'] != 3:
                for field in quant_fields:
                    total_liberado[field] += row[field]
                    if field in ['LOTES', 'QUANT']:
                        total_liberado['{}|STYLE'.format(field)] = \
                            'color: darkred;'

        data.append(total_liberado)
        data.append(total_geral)
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

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        tipo_roteiro = 'p'
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor, tipo_roteiro))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            tipo_roteiro = form.cleaned_data['tipo_roteiro']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, tipo_roteiro))
        context['form'] = form
        return render(request, self.template_name, context)


class QuantEstagio(View):
    Form_class = forms.QuantEstagioForm
    template_name = 'lotes/quant_estagio.html'
    title_name = 'Quantidades por estágio'

    def mount_context(self, cursor, estagio, ref, tipo):
        context = {
            'estagio': estagio,
            'ref': ref,
            'tipo': tipo,
        }

        data = models.quant_estagio(cursor, estagio, ref, tipo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produtos no estágio',
            })
            return context

        total = data[0].copy()
        total['REF'] = ''
        total['TAM'] = ''
        total['COR'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fields = ['LOTES', 'QUANT']
        for field in quant_fields:
            total[field] = 0
        for row in data:
            for field in quant_fields:
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
            tipo = form.cleaned_data['tipo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, estagio, ref, tipo))
        context['form'] = form
        return render(request, self.template_name, context)
