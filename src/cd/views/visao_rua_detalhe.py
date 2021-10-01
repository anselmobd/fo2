from pprint import pprint

from django.db.models import Count, Sum
from django.db.models.functions import Substr
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from utils.views import totalize_grouped_data, group_rowspan

import lotes.models
from cd.queries.visao import get_solic_dict


class VisaoRuaDetalhe(View):

    def __init__(self):
        self.template_name = 'cd/visao_rua_detalhe.html'
        self.title_name = 'Visão detalhada de rua do CD'

    def mount_context(self, rua):
        context = {'rua': rua}

        solic_dict = get_solic_dict(rua)

        locais_recs = lotes.models.Lote.objects.filter(
            local__startswith=rua
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local', 'op', 'referencia', 'cor', 'tamanho').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local', 'op', 'referencia', 'cor', 'ordem_tamanho')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'op', 'referencia', 'cor', 'tamanho', 'qlotes', 'qtdsum'))

        for row in data:
            if row['local'] in solic_dict:
                row['solicitacoes'] = ', '.join(solic_dict[row['local']])
            else:
                row['solicitacoes'] = '-'
            row['local|TARGET'] = '_BLANK'
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])

        group = ['local', 'solicitacoes']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['qlotes', 'qtdsum'],
            'count': [],
            'descr': {'op': 'Totais:'}
        })
        group_rowspan(data, group)

        headers = ['Endereço', 'Solicitações', 'OP', 'Referência', 'Cor', 'Tamanho',
                   'Lotes (caixas)', 'Qtd. itens']
        fields = ['local', 'solicitacoes', 'op', 'referencia', 'cor', 'tamanho',
                  'qlotes', 'qtdsum']

        context.update({
            'headers': headers,
            'fields': fields,
            'group': group,
            'data': data,
            'safe': ['solicitacoes'],
            'style': {6: 'text-align: right;',
                      7: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        rua = kwargs['rua'].upper()
        context = {'titulo': self.title_name}
        data = self.mount_context(rua)
        context.update(data)
        return render(request, self.template_name, context)
