from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import OpPendenteForm
import lotes.models as models


class OpPendente(View):
    Form_class = OpPendenteForm
    template_name = 'lotes/op_pendente.html'
    title_name = 'Ordens pendentes por estágio'

    def mount_context(self, cursor, estagio):
        # A ser produzido
        context = {}
        context.update({
            'estagio': estagio,
        })
        data = models.op_pendente(cursor, estagio)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem pendências',
            })
        else:
            link = ('OP')
            for row in data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
            context.update({
                'headers': (
                    'Estágio', 'Período',
                    'Referência', 'OP', 'Quantidade de peças',
                    'Quantidade de lotes'),
                'fields': (
                    'ESTAGIO', 'PERIODO',
                    'REF', 'OP', 'QTD', 'LOTES'),
                'data': data,
                'link': link,
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
