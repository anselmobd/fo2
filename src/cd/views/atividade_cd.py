from datetime import datetime
from pprint import pprint

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import geral.models
import lotes.models
from geral.functions import rec_trac_log_to_dict

import cd.forms


class AtividadeCD(View):

    def __init__(self):
        self.Form_class = cd.forms.AtividadeCDForm
        self.template_name = 'cd/atividade_cd.html'
        self.title_name = 'Atividade no CD'

    def mount_context(self, request, form):
        data_de = form.cleaned_data['data_de']
        data_ate = form.cleaned_data['data_ate']
        if not data_ate:
            data_ate = data_de

        data_ini = datetime.combine(data_de, datetime.min.time())
        data_fim = datetime.combine(data_ate, datetime.max.time())

        context = {
            'data_de': data_de,
            'data_ate': data_ate,
        }

        tracking = list(geral.models.RecordTracking.objects.filter(
            table='Lote',
            iud='u',
            log__contains='local:',
            time__gte=data_ini,
            time__lte=data_fim,
        ).order_by('time'))

        ids = [entry.record_id for entry in tracking]

        ocs = list(lotes.models.Lote.objects.filter(
            id__in=ids
        ))
        lote = {
            oc.id: oc
            for oc in ocs
        }

        dados = []
        count = 1
        for entry in tracking:
            oc = lote[entry.record_id]
            if oc.estagio < 63:
                continue
            dict_log = rec_trac_log_to_dict(entry.log, entry.log_version)
            dados.append({
                'count': count,
                'time': entry.time,
                'user': entry.user,
                'op': oc.op,
                'referencia': oc.referencia,
                'lote': oc.lote,
                'local': dict_log['local'] if dict_log['local'] else 'SAIU!',
            })
            count += 1

        context.update({
            'headers': [
                'Nº',
                'Hora',
                'OP',
                'Referência',
                'Lote',
                'Local',
                'Usuário',
            ],
            'fields': [
                'count',
                'time',
                'op',
                'referencia',
                'lote',
                'local',
                'user',
            ],
            'data': dados,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            context.update(self.mount_context(request, form))
        context['form'] = form
        return render(request, self.template_name, context)
