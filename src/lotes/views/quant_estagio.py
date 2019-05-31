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

        # informações gerais
        data = models.quant_estagio(cursor, estagio)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produtos no estágio',
            })
            return context

        context.update({
            'headers': ('REF', 'TAM', 'COR', 'QUANT'),
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
