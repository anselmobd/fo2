from pprint import pprint

from django.db.models import Count, Sum
from django.db.models.functions import Substr
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import lotes.models


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/visao_cd.html'
        self.title_name = 'Visão do CD'

    def mount_context(self):
        context = {}
        locais_recs = lotes.models.Lote.objects.all().exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).annotate(
            rua=Substr('local', 1, 1)
        ).values(
            'rua'
        ).annotate(
            qenderecos=Count('local', distinct=True),
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('rua')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'rua', 'qenderecos', 'qlotes', 'qtdsum'))

        headers = ['Rua', 'Endereços', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['rua', 'qenderecos', 'qlotes', 'qtdsum']

        total = data[0].copy()
        total['rua'] = 'Totais:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fileds = ['qenderecos', 'qlotes', 'qtdsum']
        for field in quant_fileds:
            total[field] = 0
        for row in data:
            for field in quant_fileds:
                total[field] += row[field]
            row['qenderecos|LINK'] = reverse(
                'cd:visao_rua__get', args=[row['rua']])
            row['qlotes|LINK'] = reverse(
                'cd:visao_rua_detalhe__get', args=[row['rua']])
        data.append(total)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': {2: 'text-align: right;',
                      3: 'text-align: right;',
                      4: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)
