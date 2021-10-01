from pprint import pprint

from django.db.models import Count, Sum
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import lotes.models
from cd.queries.visao import get_solic_dict


class VisaoRua(View):

    def __init__(self):
        self.template_name = 'cd/visao_rua.html'
        self.title_name = 'Visão geral de rua do CD'

    def mount_context(self, rua):
        context = {'rua': rua}

        solic_dict = get_solic_dict(rua)

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

        total = data[0].copy()
        for row in data:
            if row['local'] in solic_dict:
                row['solicitacoes'] = ', '.join(solic_dict[row['local']])
            else:
                row['solicitacoes'] = '-'
            row['local|TARGET'] = '_BLANK'
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])

        headers = ['Endereço', 'Solicitações', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['local', 'solicitacoes', 'qlotes', 'qtdsum']

        total['local'] = 'Total:'
        total['solicitacoes'] = ''
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
            'safe': ['solicitacoes'],
            'style': {3: 'text-align: right;',
                      4: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        rua = kwargs['rua'].upper()
        context = {'titulo': self.title_name}
        data = self.mount_context(rua)
        context.update(data)
        return render(request, self.template_name, context)
