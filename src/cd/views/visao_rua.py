from pprint import pprint

from django.db.models import Count, Sum
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import lotes.models


class VisaoRua(View):

    def __init__(self):
        self.template_name = 'cd/visao_rua.html'
        self.title_name = 'Visão geral de rua do CD'

    def mount_context(self, rua):
        context = {'rua': rua}
        locais_recs = lotes.models.Lote.objects.filter(
            local__startswith=rua
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'qlotes', 'qtdsum'))

        for row in data:
            row['local|TARGET'] = '_BLANK'
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])

        headers = ['Endereço', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['local', 'qlotes', 'qtdsum']

        total = data[0].copy()
        total['local'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fileds = ['qlotes', 'qtdsum']
        for field in quant_fileds:
            total[field] = 0
        for row in data:
            for field in quant_fileds:
                total[field] += row[field]
        data.append(total)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': {2: 'text-align: right;',
                      3: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        rua = kwargs['rua'].upper()
        context = {'titulo': self.title_name}
        data = self.mount_context(rua)
        context.update(data)
        return render(request, self.template_name, context)
