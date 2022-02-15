from pprint import pprint

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import lotes.models

import cd.forms


class AtividadeCD(View):

    def __init__(self):
        self.Form_class = cd.forms.AtividadeCDForm
        self.template_name = 'cd/atividade_cd.html'
        self.title_name = 'Atividade no CD'

    def mount_context(self, request, form):
        data_de = form.cleaned_data['data_de']
        context = {'data_de': data_de}

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
