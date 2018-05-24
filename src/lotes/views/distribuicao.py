import copy

from django.shortcuts import render
from django.db import connections
from django.views import View

from lotes.forms import DistribuicaoForm
import lotes.models as models


class Distribuicao(View):
    Form_class = DistribuicaoForm
    template_name = 'lotes/distribuicao.html'
    title_name = 'Distribuição'

    def mount_context(self, cursor, estagio, data_de, data_ate):
        context = {
            'estagio': estagio,
            'data_de': data_de,
            'data_ate': data_ate,
            }

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, estagio, data_de, data_ate))
        context['form'] = form
        return render(request, self.template_name, context)
