from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_conn

import lotes.models

import cd.queries as queries


class InconsistenciasDetalhe(View):

    def __init__(self):
        self.template_name = 'cd/inconsist_detalhe.html'
        self.title_name = 'Detalhe de inconsistência'

    def mount_context(self, cursor, op):
        context = {'op': op}

        lotes_recs = lotes.models.Lote.objects.filter(
            op=op
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('lote').distinct()
        if len(lotes_recs) == 0:
            return context

        ocs = []
        for lote in lotes_recs:
            ocs.append(lote['lote'][4:].lstrip('0'))

        headers = ['Estágio', 'Lote', 'Referência', 'Cor', 'Tamanho',
                   'Quantidade']
        fields = ['est', 'lote', 'ref', 'cor', 'tam', 'qtd']

        data = queries.inconsistencias_detalhe(cursor, op, ocs)

        for row in data:
            if row['seq'] == 99:
                row['est'] = 'Finalizado'
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        data63 = queries.inconsistencias_detalhe(cursor, op, ocs, est63=True)

        for row in data63:
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers63': headers,
            'fields63': fields,
            'data63': data63,
        })

        return context

    def get(self, request, *args, **kwargs):
        op = int(kwargs['op'])

        context = {'titulo': self.title_name}
        cursor = db_conn('so', request).cursor()
        data = self.mount_context(cursor, op)
        context.update(data)
        return render(request, self.template_name, context)
